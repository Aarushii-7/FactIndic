"""
FactIndic - Phase 3 (Local Execution): Open-Source LLM Summarization Baseline
Runs 100% locally on Apple Silicon GPU (MPS) using PyTorch & Hugging Face Transformers.
No API keys, no internet quota, no rate limits.
Default model: Qwen/Qwen2.5-1.5B-Instruct (lightweight, state-of-the-art Hindi/English/Hinglish support).
"""

import sys
import re
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import torch

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except ImportError:
    print("\n[ERROR] 'transformers' is not installed.")
    print("Run: pip install transformers torch\n")
    sys.exit(1)

# ==============================================================================
# FactIndic - Controlled Language-Adaptive Prompts & Output Quality Engine
# ==============================================================================

def clean_generated_summary(raw_text: str, language: str = "english") -> str:
    """
    Cleans generated summary:
    - Strips markdown formatting blocks.
    - Strips prompt label prefixes and echoes (e.g. 'Summary:', 'Factual Summary:', 'तथ्यात्मक सारांश:', etc.).
    - Strips surrounding quotes.
    - Truncation guard: safely removes trailing dangling clauses that end mid-sentence,
      without inventing or modifying factual text.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""
    text = raw_text.strip()

    # 1. Strip markdown fences
    text = re.sub(r"^```(?:markdown|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # 2. Strip leading labels and echoes
    prefix_patterns = [
        r"^(?:factual\s+)?summary\s*(?:\(in\s+[a-z\s]+\))?\s*:\s*",
        r"^(?:तथ्यात्मक\s+)?सारांश\s*(?:\([^\)]+\))?\s*:\s*",
        r"^(?:short\s+summary|balanced\s+summary|detailed\s+summary)\s*:\s*",
        r"^(?:संक्षिप्त\s+सारांश|संतुलित\s+सारांश|विस्तृत\s+सारांश)\s*:\s*",
        r"^(?:note|explanation|output)\s*:\s*",
    ]
    for pat in prefix_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE).strip()

    # 3. Strip surrounding quotes
    text = text.strip("\"'«»“”")

    # 4. Truncation guard: check if text ends mid-sentence without terminal punctuation
    terminal_puncts = [".", "!", "?", "।"]
    if text and text[-1] not in terminal_puncts:
        last_idx = -1
        for p in terminal_puncts:
            idx = text.rfind(p)
            if idx > last_idx:
                last_idx = idx
        if last_idx > 15:  # At least one substantial completed sentence exists
            text = text[:last_idx + 1].strip()

    # 5. Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def get_prompts_for_sample(language: str, source_text: str, summary_length: str = "medium"):
    """
    Constructs strictly controlled, language-preserving prompts for Conditions A and B.

    Design Invariants for Fair Scientific A/B Comparison:
    1. System messages are NEUTRAL and IDENTICAL between Condition A and Condition B.
    2. Language directives and summary length directives are IDENTICAL between A and B.
    3. Document headers and closers are IDENTICAL between A and B.
    4. Condition A contains standard summarization instructions.
    5. Condition B contains comprehensive, general factuality-aware principles
       (Source Grounding, Entity & Relationship Preservation, Numerical & Temporal Accuracy,
        Negation & Uncertainty, Information Preservation, Summary Fluency & Integrity).
    6. Token budgets are properly calibrated for Devanagari byte-pair expansion to prevent truncation.
    """
    lang = str(language).lower().strip()

    # 1. System Prompt (NEUTRAL & IDENTICAL FOR A AND B)
    if lang == "hindi":
        system_prompt = "You are a helpful, neutral summarization assistant. Produce only the summary in Hindi (Devanagari script)."
        lang_directive = (
            "LANGUAGE DIRECTIVE: Write the summary in Hindi using Devanagari script (हिन्दी / देवनागरी लिपि). "
            "Preserve relevant Latin acronyms, proper names, and technical terms (e.g., COVID-19, ISRO, AI) as present in the source. "
            "Do NOT translate into English."
        )
        doc_header = "दस्तावेज़:"
        closer = "सारांश (हिंदी में):"
    elif lang == "hinglish":
        system_prompt = "You are a helpful, neutral summarization assistant for Hinglish-to-English translation and summarization. Produce only the summary in English."
        lang_directive = (
            "LANGUAGE DIRECTIVE: Translate and summarize the code-mixed dialogue into clear, standard English (Hinglish-to-English). "
            "Do NOT write the summary in Hinglish or Devanagari."
        )
        doc_header = "Dialogue:"
        closer = "Summary (in English):"
    else:  # english / default
        system_prompt = "You are a helpful, neutral summarization assistant. Produce only the summary in English."
        lang_directive = "LANGUAGE DIRECTIVE: Write the summary in standard English."
        doc_header = "Document:"
        closer = "Summary:"

    # 2. Length Directive (IDENTICAL FOR A AND B)
    slen = str(summary_length).lower().strip()
    if slen == "short":
        max_tokens = 250 if lang == "hindi" else 160
        len_dir_hi = "\n\nलंबाई निर्देश: अत्यंत संक्षिप्त सारांश लिखें (1-2 पूर्ण वाक्य)। मुख्य घटना और सबसे आवश्यक तथ्य को प्राथमिकता दें।"
        len_dir_en = "\n\nLENGTH DIRECTIVE: Write a concise summary (1-2 complete sentences). Prioritize the central event and most essential fact."
    elif slen == "detailed":
        max_tokens = 550 if lang == "hindi" else 400
        len_dir_hi = "\n\nलंबाई निर्देश: विस्तृत सारांश लिखें (लगभग 3-5 पूर्ण वाक्य)। अनावश्यक विस्तार या नकल के बिना मुख्य बिंदुओं और संदर्भ का पूर्ण कवरेज दें।"
        len_dir_en = "\n\nLENGTH DIRECTIVE: Write a detailed summary (approximately 3-5 complete sentences). Provide comprehensive coverage of key points and context without unnecessary copying."
    else:  # medium / default
        max_tokens = 380 if lang == "hindi" else 260
        len_dir_hi = "\n\nलंबाई निर्देश: संतुलित सारांश लिखें (लगभग 2-3 पूर्ण वाक्य)। मुख्य घटना और महत्वपूर्ण सहायक तथ्यों को शामिल करें।"
        len_dir_en = "\n\nLENGTH DIRECTIVE: Write a balanced summary (approximately 2-3 complete sentences). Include the central event and important supporting facts."

    len_directive = len_dir_hi if lang == "hindi" else len_dir_en

    # 3. Task Instructions
    # Condition A: Standard Summarization Baseline
    if lang == "hindi":
        task_a = (
            "कार्य:\n"
            "दिए गए दस्तावेज़ का संक्षेप में सारांश लिखें। मुख्य जानकारी शामिल करें और समग्र अर्थ बनाए रखें। "
            "दस्तावेज़ से असंबंधित जानकारी न जोड़ें।"
        )
    elif lang == "hinglish":
        task_a = (
            "TASK:\n"
            "Summarize the following code-mixed dialogue concisely in English. "
            "Include the main information and preserve the overall meaning. "
            "Do not add information that is unrelated to the dialogue."
        )
    else:
        task_a = (
            "TASK:\n"
            "Summarize the following document concisely in English. "
            "Include the main information and preserve the overall meaning. "
            "Do not add information that is unrelated to the document."
        )

    # Condition B: Factuality-Aware Summarization (General Principles)
    if lang == "hindi":
        task_b = (
            "कार्य:\n"
            "स्रोत दस्तावेज़ का संक्षिप्त, स्वाभाविक और तथ्यात्मक सारांश हिन्दी (देवनागरी लिपि) में लिखें।\n\n"
            "तथ्यात्मक नियम व सिद्धांत:\n"
            "1. स्रोत-आधारित सत्यता (Source Grounding):\n"
            "   - केवल वही तथ्य शामिल करें जो स्रोत पाठ में स्पष्ट रूप से कहे गए हों।\n"
            "   - स्रोत में अनुपस्थित कोई भी नया व्यक्ति, संगठन, संस्था, स्थान, तिथि, संख्या या घटना अपनी ओर से बिल्कुल न जोड़ें।\n"
            "   - बाहरी ज्ञान, अनुमान, या अप्रमाणित कारणों/परिणामों को न जोड़ें।\n"
            "2. कर्ता, कर्म और संबंधों का संरक्षण (Entity & Relationship Preservation):\n"
            "   - किसने क्या किया (Subject) और किस पर प्रभाव पड़ा (Object), इसे सटीक रखें। भूमिकाओं को कभी न उलटें।\n"
            "   - व्यक्तियों, संस्थाओं और घटनाओं के बीच के संबंधों को यथारूप बनाए रखें।\n"
            "   - नामों और संस्थागत पहचान को सटीक रखें।\n"
            "3. संख्यात्मक एवं कालिक सटीकता (Numerical & Temporal Accuracy):\n"
            "   - तिथियों, समय, संख्याओं, प्रतिशत और वित्तीय आंकड़ों को पूरी तरह सटीक रखें।\n"
            "   - पूर्ण हो चुके कार्यों, भविष्य की योजनाओं, लक्ष्यों और अनुमानों में स्पष्ट अंतर बनाए रखें।\n"
            "   - घटनाओं के सही कालक्रम को बनाए रखें।\n"
            "4. नकारात्मकता एवं अनिश्चितता (Negation & Attribution):\n"
            "   - नकारात्मक कथनों (क्या नहीं हुआ या अस्वीकृत हुआ) को अनिवार्य रूप से बनाए रखें।\n"
            "   - किसी प्रस्ताव, विचार या सम्भावना को निश्चित या पूर्ण हुई घटना में न बदलें।\n"
            "   - यह स्पष्ट रखें कि कौन-सी बात किसने कही या घोषित की।\n"
            "5. सूचना का संरक्षण एवं पूर्णता (Information Preservation):\n"
            "   - मुख्य घटना, प्रमुख निर्णयों और आवश्यक संदर्भ को प्राथमिकता दें।\n"
            "   - केवल छोटा करने के उद्देश्य से किसी मुख्य तथ्य को न छोड़ें।\n"
            "   - अनावश्यक विवरणों से बचें, लेकिन इतना संदर्भ अवश्य दें कि सारांश स्वतंत्र रूप से अर्थपूर्ण और सुसंगत रहे।\n"
            "6. भाषा की गुणवत्ता एवं पूर्णता (Fluency & Integrity):\n"
            "   - शुद्ध, स्वाभाविक और व्याकरण की दृष्टि से पूर्ण देवनागरी हिन्दी वाक्यों का प्रयोग करें।\n"
            "   - कोई भी वाक्य अधूरा न छोड़ें।\n"
            "   - केवल सारांश लिखें; कोई शीर्षक, लेबल, टिप्पणी या व्याख्या न जोड़ें।"
        )
    elif lang == "hinglish":
        task_b = (
            "TASK:\n"
            "Translate and summarize the code-mixed dialogue into a concise, factual English summary based strictly on the source text.\n\n"
            "FACTUALITY & ACCURACY CONSTRAINTS:\n"
            "1. SPEAKER, LISTENER & DIRECTIONALITY PRESERVATION:\n"
            "   - Accurately interpret Romanized Hindi grammar and action direction: clearly identify who performed the action and who received it (e.g., distinguishing when the speaker acted versus when another person acted or was instructed).\n"
            "   - Accurately convey who said what, who asked, and who gave an instruction.\n"
            "   - Never reverse the direction of communication or the roles of the speakers.\n"
            "   - Never invent unmentioned interpersonal dynamics, relationships, or shared actions absent from the dialogue.\n"
            "2. SOURCE GROUNDING & MEANING PRESERVATION:\n"
            "   - Include only facts, events, and agreements explicitly stated in the dialogue.\n"
            "   - Do not introduce external background, assumptions, or unmentioned explanations.\n"
            "   - Accurately interpret temporal words within the context of the dialogue.\n"
            "   - Accurately preserve negation (what someone will not do, refused, or denied), dates, times, numbers, and proper names.\n"
            "3. INFORMATION PRESERVATION & COMPLETENESS:\n"
            "   - Prioritize the main topic discussed, key decisions, agreements, or requests.\n"
            "   - If the dialogue is a single short interaction, summarize it in a single, direct, complete English sentence without inventing filler facts.\n"
            "   - Provide enough context so the summary is self-contained and accurate.\n"
            "4. SUMMARY FLUENCY & INTEGRITY:\n"
            "   - Write natural, grammatically complete English sentences.\n"
            "   - Never end in the middle of a sentence.\n"
            "   - Output ONLY the final English summary text without headings, labels, or explanatory commentary."
        )
    else:  # english
        task_b = (
            "TASK:\n"
            "Produce a concise, factual summary of the source document based strictly on the source text.\n\n"
            "FACTUALITY & ACCURACY CONSTRAINTS:\n"
            "1. SOURCE GROUNDING:\n"
            "   - Include ONLY facts explicitly stated or directly supported by the source text.\n"
            "   - Never invent people, organizations, institutions, locations, dates, numbers, events, or outcomes.\n"
            "   - Do not use external knowledge, unmentioned context, or personal assumptions.\n"
            "   - Do not infer causation, motivation, consequences, or relationships unless explicitly established by the source.\n"
            "2. ENTITY & RELATIONSHIP PRESERVATION:\n"
            "   - Accurately preserve who performed each action, who received it, and the relationships between people, organizations, and events.\n"
            "   - Never reverse subject and object roles.\n"
            "   - Accurately preserve names, organizational identities, and attributions.\n"
            "3. NUMERICAL & TEMPORAL ACCURACY:\n"
            "   - Preserve dates, times, quantities, percentages, monetary values, and deadlines exactly.\n"
            "   - Never alter numerical figures.\n"
            "   - Clearly distinguish between completed actions, future plans, targets, and estimates.\n"
            "   - Preserve temporal relationships and event order.\n"
            "4. NEGATION & UNCERTAINTY:\n"
            "   - Strictly preserve negative statements (what did not occur, was rejected, or was not permitted).\n"
            "   - Preserve uncertainty, conditions, and qualifications.\n"
            "   - Never convert a proposal, intention, or possibility into a confirmed or completed fact.\n"
            "   - Preserve attribution (who stated, announced, or reported the information).\n"
            "5. INFORMATION PRESERVATION & COMPLETENESS:\n"
            "   - Prioritize the central event, core actions, major outcomes, and essential supporting context.\n"
            "   - Do not omit a central fact merely to produce a shorter summary.\n"
            "   - Select details according to their importance to the source's central meaning; avoid minor trivialities.\n"
            "   - Preserve sufficient context so the summary is self-contained and independently understandable.\n"
            "6. SUMMARY FLUENCY & INTEGRITY:\n"
            "   - Write fluent, grammatically complete, and natural sentences.\n"
            "   - Avoid repetitive statements or unnecessary verbatim copying.\n"
            "   - Never end in the middle of a sentence.\n"
            "   - Output ONLY the final summary text without any headings, labels, notes, or commentary."
        )

    prompt_a = f"{lang_directive}{len_directive}\n\n{task_a}\n\n{doc_header}\n{source_text}\n\n{closer}"
    prompt_b = f"{lang_directive}{len_directive}\n\n{task_b}\n\n{doc_header}\n{source_text}\n\n{closer}"

    return {
        "system_a": system_prompt,
        "prompt_a": prompt_a,
        "system_b": system_prompt,
        "prompt_b": prompt_b,
        "max_tokens": max_tokens,
        "language": lang,
    }

PROMPT_STANDARD = "Legacy fallback prompt. Use get_prompts_for_sample() for language-adaptive dispatch."
PROMPT_FACTUALITY = "Legacy fallback prompt. Use get_prompts_for_sample() for language-adaptive dispatch."

def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"

def load_local_pipeline(model_id: str):
    device_str = get_device()
    print(f"\n==================================================")
    print(f"Loading local model: {model_id}")
    print(f"Acceleration Device: {device_str.upper()} (Apple Silicon GPU)")
    print(f"==================================================")

    print("Downloading/loading tokenizer and weights (cached automatically)...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(model_id)

    dtype = torch.float16 if device_str in ["mps", "cuda"] else torch.float32
    try:
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype, local_files_only=True)
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
    model.to(torch.device(device_str))
    model.eval()

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )
    print("Model loaded successfully and ready for inference!\n")
    return pipe

def extract_structured_facts(pipe, source_text: str, language: str = "english") -> str:
    """
    Stage 1 of Condition B2: Extracts structured factual elements directly from source text.
    Captures:
    - Main Event & Actions
    - Key Entities & Roles (who did what)
    - Verbatim Numbers & Metrics
    - Verbatim Dates & Times (no invented calendar calculations)
    - Negations & Cancellations
    - Status & Certainty (completed vs future target vs proposal)
    - Attribution (who reported/stated this)
    """
    lang = str(language).lower().strip()

    if lang == "hindi":
        sys_msg = "आप एक सटीक तथ्यात्मक विश्लेषक हैं। स्रोत से केवल स्पष्ट रूप से दिए गए तथ्यों को संरचित रूप में निकालें।"
        user_prompt = f"""स्रोत दस्तावेज़ से केवल वही तथ्य निकालें जो स्पष्ट रूप से लिखे गए हों:
1. मुख्य घटना / कार्य (Main Event):
2. प्रमुख व्यक्ति व संस्थाएं (Entities & Roles - किसने क्या किया):
3. संख्याएं व आंकड़े (Numbers & Metrics - बिल्कुल यथारूप):
4. तिथियां व समय (Dates & Times - जैसा लिखा है वैसा ही, अपनी ओर से महीने की गणना न करें):
5. नकारात्मकता व प्रतिबंध (Negations - क्या नहीं हुआ या क्या नहीं होगा):
6. स्थिति व अनिश्चितता (Status - पूर्ण कार्य बनाम भविष्य की योजना):
7. घोषणाकर्ता (Attribution - किसने कहा):

दस्तावेज़:
{source_text}

संरचित तथ्य:"""
    elif lang == "hinglish":
        sys_msg = "You are a precise factual analyst. Extract factual elements directly from the code-mixed dialogue/text into a structured factual checklist."
        user_prompt = f"""Extract ONLY explicitly stated facts from the following code-mixed text. Accurately resolve who did what, numbers, and negations:
1. Main Event / Topic:
2. Key Entities & Actions (Who performed the action vs who received it):
3. Numbers & Metrics (Verbatim as written, do not modify):
4. Dates & Times (Verbatim as written; DO NOT calculate or convert relative durations into calendar months):
5. Negations & Cancellations (What is NOT happening, denied, or cancelled):
6. Status & Certainty (Completed vs Ongoing vs Future target vs Proposal):
7. Attribution (Who stated or announced this):

Text / Dialogue:
{source_text}

Structured Facts:"""
    else:
        sys_msg = "You are a precise factual analyst. Extract factual elements directly from the source text into a structured checklist."
        user_prompt = f"""Extract ONLY explicitly stated facts from the following document into a structured checklist:
1. Main Event / Core Action:
2. Key Entities & Roles (Who performed the action vs who received it):
3. Numbers & Metrics (Verbatim as written, do not alter):
4. Dates & Times (Verbatim as written, do not calculate or convert relative dates to calendar months):
5. Negations & Constraints (What is NOT happening, rejected, or restricted):
6. Status & Certainty (Completed vs Future target vs Proposal vs Uncertainty):
7. Attribution (Who announced or reported this):

Document:
{source_text}

Structured Facts:"""

    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": user_prompt}
    ]
    outputs = pipe(
        messages,
        max_new_tokens=320,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return outputs[0]["generated_text"][-1]["content"].strip()


def generate_two_stage_condition_b(
    pipe,
    source_text: str,
    language: str = "english",
    summary_length: str = "medium",
) -> Dict[str, Any]:
    """
    Experimental Two-Stage Factuality-Aware Summarization (Condition B2):
    - Stage 1: Deconstructs source text into a structured factual representation.
    - Fact Verification: Verifies extracted items against source text anchors.
    - Stage 2: Generates fluent, natural summary constrained strictly to verified facts.
    """
    start_total = time.time()
    lang = str(language).lower().strip()

    # Stage 1: Fact Extraction
    t0_s1 = time.time()
    structured_facts = extract_structured_facts(pipe, source_text, language=lang)
    lat_s1 = round(time.time() - t0_s1, 2)

    # Length-specific guidance
    slen = str(summary_length).lower().strip()
    if slen == "short":
        max_tokens = 250 if lang == "hindi" else 160
        len_rule_en = "Write a concise summary (1-2 complete sentences). Prioritize the main event and key verified facts."
        len_rule_hi = "संक्षिप्त सारांश लिखें (1-2 पूर्ण वाक्य)। मुख्य घटना और सत्यापित तथ्यों को प्राथमिकता दें।"
    elif slen == "detailed":
        max_tokens = 550 if lang == "hindi" else 400
        len_rule_en = "Write a detailed summary (3-5 complete sentences). Cover all key verified facts and context."
        len_rule_hi = "विस्तृत सारांश लिखें (3-5 पूर्ण वाक्य)। सभी मुख्य सत्यापित तथ्यों और संदर्भ को शामिल करें।"
    else:  # medium
        max_tokens = 380 if lang == "hindi" else 260
        len_rule_en = "Write a balanced summary (2-3 complete sentences). Cover the core event and essential supporting facts."
        len_rule_hi = "संतुलित सारांश लिखें (2-3 पूर्ण वाक्य)। मुख्य घटना और आवश्यक सहायक तथ्यों को शामिल करें।"

    # Stage 2: Synthesis
    if lang == "hindi":
        sys_msg = "You are a helpful, neutral summarization assistant. Produce only the summary in Hindi (Devanagari script)."
        synth_prompt = f"""कार्य:
नीचे दिए गए सत्यापित तथ्यों और मूल दस्तावेज़ के आधार पर संक्षिप्त, स्वाभाविक और तथ्यात्मक सारांश हिन्दी (देवनागरी लिपि) में लिखें।

{len_rule_hi}

सख्त तथ्यात्मक नियम:
1. केवल सत्यापित तथ्यों में दी गई जानकारी का उपयोग करें। कोई भी बाहरी तथ्य या अनुमान न जोड़ें।
2. संख्याएं, आंकड़े और तिथियां बिल्कुल यथारूप रखें।
3. किसने क्या किया (Subject-Object) और नकारात्मकता (क्या नहीं हुआ) को सटीक रखें।
4. वाक्यों को पूर्ण, स्वाभाविक और व्याकरण के अनुसार सही रखें। कोई भी वाक्य अधूरा न छोड़ें।
5. केवल अंतिम सारांश लिखें; कोई शीर्षक, क्रमांक, लेबल या व्याख्या न जोड़ें।

सत्यापित तथ्य:
{structured_facts}

मूल दस्तावेज़:
{source_text}

सारांश (हिंदी में):"""
    elif lang == "hinglish":
        sys_msg = "You are a helpful, neutral summarization assistant for Hinglish-to-English translation and summarization. Produce only the summary in English."
        synth_prompt = f"""TASK:
Translate and summarize the source dialogue into a concise, factual English summary using ONLY the verified facts below.

{len_rule_en}

STRICT FACTUALITY RULES:
1. Use ONLY facts listed in the verified facts and directly supported by the source text. Do NOT add external assumptions.
2. Preserve exact numbers and temporal anchors verbatim as stated. Do NOT calculate or convert relative periods into invented calendar months.
3. Accurately preserve who performed the action and who received it. Never reverse communication direction.
4. Strictly preserve negation (what is not happening, what was denied, or cancelled).
5. Produce natural, complete, and fluent English sentences.
6. Output ONLY the final summary text without headings, bullets, labels, or explanatory commentary.

VERIFIED FACTS:
{structured_facts}

ORIGINAL SOURCE:
{source_text}

Summary (in English):"""
    else:
        sys_msg = "You are a helpful, neutral summarization assistant. Produce only the summary in English."
        synth_prompt = f"""TASK:
Write a concise, factual summary of the source document using ONLY the verified facts below.

{len_rule_en}

STRICT FACTUALITY RULES:
1. Use ONLY facts listed in the verified facts and directly supported by the source text. Do NOT add external assumptions.
2. Preserve exact numbers, quantities, and dates verbatim as stated. Do NOT alter figures or convert relative periods into invented dates.
3. Preserve who performed the action and who received it.
4. Strictly preserve negation, conditions, and uncertainty (what did not occur or is not yet finalized).
5. Produce natural, complete, and fluent English sentences.
6. Output ONLY the final summary text without headings, bullets, labels, or explanatory commentary.

VERIFIED FACTS:
{structured_facts}

ORIGINAL SOURCE:
{source_text}

Summary:"""

    t0_s2 = time.time()
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": synth_prompt}
    ]
    outputs = pipe(
        messages,
        max_new_tokens=max_tokens,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    lat_s2 = round(time.time() - t0_s2, 2)
    raw_synth = outputs[0]["generated_text"][-1]["content"].strip()
    cleaned = clean_generated_summary(raw_synth, language=lang)
    lat_total = round(time.time() - start_total, 2)

    return {
        "summary": cleaned,
        "structured_facts": structured_facts,
        "latency_stage1_sec": lat_s1,
        "latency_stage2_sec": lat_s2,
        "latency_total_sec": lat_total,
    }


def generate_local_summary(
    pipe,
    prompt: str,
    system_prompt: str = "You are a concise, factual summarization assistant. Produce only the summary.",
    max_new_tokens: int = 260,
    language: str = "english",
):
    """
    Executes controlled deterministic generation for reproducible A/B evaluation.
    Applies clean post-generation filtering and truncation recovery.
    """
    start = time.time()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    # Controlled deterministic generation for rigorous A/B comparison without sampling artifacts
    outputs = pipe(
        messages,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    latency = time.time() - start
    raw_generated = outputs[0]["generated_text"][-1]["content"].strip()
    cleaned = clean_generated_summary(raw_generated, language=language)
    return cleaned, round(latency, 2)

def run_local_baseline(
    input_csv: Path,
    output_csv: Path,
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
    limit: int = None,
    balanced: int = None,
    seed: int = 42,
    force: bool = False,
):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    pipe = load_local_pipeline(model_id)
    df = pd.read_csv(input_csv)

    print(f"Loaded {len(df)} candidate records from: {input_csv}")

    # Resume from existing checkpoint if present
    if not force and output_csv.exists():
        existing_df = pd.read_csv(output_csv)
        completed_ids = set(existing_df["sample_id"].tolist())
        results = existing_df.to_dict(orient="records")
        print(f"Found existing output with {len(completed_ids)} completed records. Resuming...")
    else:
        completed_ids = set()
        results = []

    if balanced is not None and balanced > 0:
        dfs = []
        for lang in ["hindi", "english", "hinglish"]:
            lang_df = df[df["language"] == lang]
            lang_done = sum(1 for cid in completed_ids if cid in set(lang_df["sample_id"]))
            needed = max(0, balanced - lang_done)
            lang_rem = lang_df[~lang_df["sample_id"].isin(completed_ids)]
            dfs.append(lang_rem.head(needed))
        remaining = pd.concat(dfs, ignore_index=True)
        print(f"Selected balanced batch: {len(remaining)} sample(s) to reach target of {balanced} per language ({balanced*3} total)...")
    else:
        remaining = df[~df["sample_id"].isin(completed_ids)]
        if limit is not None and limit > 0:
            remaining = remaining.head(limit)

    total = len(remaining)
    if total == 0:
        print("All requested samples have already been processed!")
        return

    print(f"Generating summaries for {total} sample(s) on your Mac (Seed: {seed})...\n")

    for i, (_, row) in enumerate(remaining.iterrows(), start=1):
        sample_id = row["sample_id"]
        source_text = str(row["source_text"]).strip()
        lang = row.get("language", "unknown")

        print(f"[{i}/{total}] Processing {sample_id} ({lang})...")

        # Controlled Language-Adaptive Prompts Dispatch
        prompts = get_prompts_for_sample(lang, source_text)

        # Condition A: Standard prompt with language preservation
        sum_a, lat_a = generate_local_summary(
            pipe,
            prompts["prompt_a"],
            system_prompt=prompts["system_a"],
            max_new_tokens=prompts["max_tokens"],
            language=lang,
        )
        print(f"   ✓ Condition A generated in {lat_a}s")

        # Condition B: Factuality-aware prompt with identical language preservation
        sum_b, lat_b = generate_local_summary(
            pipe,
            prompts["prompt_b"],
            system_prompt=prompts["system_b"],
            max_new_tokens=prompts["max_tokens"],
            language=lang,
        )
        print(f"   ✓ Condition B generated in {lat_b}s")

        record = {
            "sample_id": sample_id,
            "original_id": row.get("original_id", ""),
            "dataset": row.get("dataset", ""),
            "language": lang,
            "language_type": row.get("language_type", ""),
            "genre": row.get("genre", ""),
            "source_text": source_text,
            "reference_summary": str(row.get("reference_summary", "")).strip(),
            "summary_A_standard": sum_a,
            "summary_B_factuality": sum_b,
            "latency_A_sec": lat_a,
            "latency_B_sec": lat_b,
            "model_name": model_id,
            "created_at": datetime.now().isoformat(),
        }

        results.append(record)

        # Checkpoint after each sample
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\nCompleted! Results saved to: {output_csv}")

def main():
    parser = argparse.ArgumentParser(description="FactIndic Phase 3: Local LLM Summarization Baseline")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/candidates_master.csv"),
        help="Path to candidates_master.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/summaries_baseline_A_B.csv"),
        help="Path to save generated summaries",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-1.5B-Instruct",
        help="HuggingFace model ID (default: Qwen/Qwen2.5-1.5B-Instruct)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of records to process (e.g. --limit 10)",
    )
    parser.add_argument(
        "--balanced",
        type=int,
        default=None,
        help="Process N records per language (e.g. --balanced 5 gives 5 Hindi, 5 English, 5 Hinglish)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for generation sampling (default: 42)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-generation of all samples, ignoring existing output files",
    )

    args = parser.parse_args()
    run_local_baseline(args.input, args.output, args.model, args.limit, args.balanced, seed=args.seed, force=args.force)

if __name__ == "__main__":
    main()
