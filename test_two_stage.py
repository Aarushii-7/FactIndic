import re
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_id = "Qwen/Qwen2.5-1.5B-Instruct"
device = "mps" if torch.backends.mps.is_available() else "cpu"
dtype = torch.float16 if device in ["mps", "cuda"] else torch.float32

print(f"Loading {model_id} on {device}...")
tok = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
model.to(torch.device(device))
model.eval()
pipe = pipeline("text-generation", model=model, tokenizer=tok)
print("Pipeline loaded.")

def extract_structured_facts(pipe, source_text: str, language: str = "english"):
    lang = language.lower()
    
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
3. Numbers & Metrics (Verbatim as written):
4. Dates & Times (Verbatim as written; DO NOT convert relative durations into calendar months):
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
4. Dates & Times (Verbatim as written, do not convert relative dates to months):
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
        max_new_tokens=300,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return outputs[0]["generated_text"][-1]["content"].strip()

# Test with FreshRoute
src_fresh = "Bengaluru-based startup FreshRoute ne 19 November 2026 ko apni grocery delivery service launch ki. Company ke founder Rohan Mehta ne bataya ki initially service Bengaluru ke 7 areas mein available hogi. Startup ne ab tak 42 local farmers aur 18 delivery partners ke saath agreements sign kiye hain. Customers ko order place karne ke 12 se 24 hours ke andar delivery provide karne ka target rakha gaya hai. Company ka aim hai ki first four months mein 3,500 customers tak reach kiya ja sake. Rohan ne kaha ki company abhi doosre cities mein expansion plan finalize nahi kar rahi hai. Delivery charges aur minimum order value ki details next week announce ki jayengi."

print("\n--- STAGE 1: FACT EXTRACTION ---")
facts = extract_structured_facts(pipe, src_fresh, language="hinglish")
print(facts)
