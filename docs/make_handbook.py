import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


import re

def clean_xml(s):
    if not isinstance(s, str):
        return s
    tokens = re.split(r'(</?[bi]>|<br\s*/>|</?code>)', s)
    out = []
    for t in tokens:
        if t in ['<b>', '</b>', '<i>', '</i>', '<br/>', '<br />', '<code>', '</code>']:
            out.append(t)
        else:
            t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            out.append(t)
    return ''.join(out)

def SafeParagraph(text, style, **kwargs):
    return Paragraph(clean_xml(text), style, **kwargs)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(36, 756, "FACTINDIC: Factuality-Aware Summarization for Indic & Code-Mixed Languages")
            self.setFont("Helvetica", 8)
            self.drawRightString(576, 756, "CSET 346 Team Handbook & Viva Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)
            
            self.line(36, 42, 576, 42)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 30, "Bennett University • Computer Science & Engineering • Dr. Geetanjali Singh")
            self.drawRightString(576, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_handbook():
    pdf_path = "/Users/aarushi/factIndic/docs/FACTINDIC_PRESENTATION_AND_VIVA_HANDBOOK.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'),
        alignment=0,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4338CA'),
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4338CA'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        borderPadding=4,
        spaceAfter=5
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E1B4B')
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    q_style = ParagraphStyle(
        'Viva_Q',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    a_style = ParagraphStyle(
        'Viva_A',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    story = []

    def add_callout(text, bg="#EEF2FF", border="#818CF8"):
        p = SafeParagraph(f"<b>Key Takeaway:</b> {text}", callout_style)
        t = Table([[p]], colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border)),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(Spacer(1, 3))
        story.append(t)
        story.append(Spacer(1, 5))

    # COVER / HEADER
    story.append(SafeParagraph("FACTINDIC", title_style))
    story.append(SafeParagraph("Factuality-Aware Summarization & Verification System for Indic & Code-Mixed Text", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4338CA"), spaceAfter=8))
    
    meta_table_data = [
        [
            SafeParagraph("<b>Course:</b> CSET 346 – Natural Language Processing<br/><b>Faculty Guide:</b> Dr. Geetanjali Singh<br/><b>Institution:</b> Bennett University (Times Group)", meta_style),
            SafeParagraph("<b>Team Members & Responsibilities:</b><br/>• <b>Rishika:</b> Datasets & NLP Preprocessing<br/>• <b>Simran:</b> Summarization Model & Prompt Engineering<br/>• <b>Aarushi:</b> Factuality Verification & Targeted Revision<br/>• <b>Khanak:</b> Evaluation & Research Analysis<br/>• <b>Hina:</b> Frontend, Backend Integration & Deployment", meta_style),
            SafeParagraph("<b>Evaluation Benchmark:</b> N = 500 Samples<br/><b>Languages:</b> Hindi, Hinglish, English<br/><b>Primary LLM:</b> Qwen2.5-1.5B-Instruct<br/><b>NLI Engine:</b> mDeBERTa-v3-base-xnli<br/><b>Date:</b> November 2026", meta_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[180, 190, 170])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # TABLE OF CONTENTS SUMMARY
    toc_p = SafeParagraph("<b>Document Structure:</b> Part 1: Project Reality Check & Code Audit | Part 2: Core NLP & Problem Motivation | Part 3: Architecture & Execution Flow | Part 4: Individual Team Member Deep Dives (Rishika, Simran, Aarushi, Khanak, Hina) | Part 5: End-to-End Live Demonstration Script | Part 6: Condition A vs B vs C Comparison | Part 7: Tech Stack Matrix | Part 8: 110-Question Viva Question Bank | Part 9: Spoken Presentation Scripts | Part 10: Last-Minute Cram Sheet.", body_style)
    story.append(toc_p)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=8))

    # =========================================================================
    # PART 1 — REPOSITORY AUDIT & IMPLEMENTATION REALITY CHECK
    # =========================================================================
    story.append(SafeParagraph("PART 1: Repository Audit & Implementation Reality Check", h1_style))
    story.append(SafeParagraph("To ensure technical rigor during evaluation, every feature is explicitly audited against the verified repository codebase. The team makes no claims regarding features that were not fully verified in code.", body_style))
    
    audit_data = [
        [SafeParagraph("Feature / Component", table_header), SafeParagraph("Implementation Status", table_header), SafeParagraph("Repository Source File & Implementation Evidence", table_header)],
        [SafeParagraph("Local Qwen Summarization", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("generate_summaries_local.py runs Qwen/Qwen2.5-1.5B-Instruct locally via PyTorch on Apple Silicon MPS device. Decodes temperature=0.2.", table_cell)],
        [SafeParagraph("3 Experimental Conditions (A/B/C)", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("A: Standard Baseline; B: Factuality-Aware with negative constraints; C: NLI-guided targeted in-place revision loop.", table_cell)],
        [SafeParagraph("Atomic Claim Extraction", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("src/claim_extractor.py: rule_based_claim_split splits on sentence boundaries (.!?।\\n;—) and contrastive clauses (while, whereas, जबकि, परन्तु).", table_cell)],
        [SafeParagraph("Multilingual Evidence Retrieval", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("src/evidence_retriever.py: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 encodes units into 384-dim dense vectors, computing cosine similarity.", table_cell)],
        [SafeParagraph("Cross-Lingual NLI Verification", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("src/nli_verifier.py: MoritzLaurer/mDeBERTa-v3-base-xnli classifies premise-hypothesis pairs into Entailment, Contradiction, Neutral with calibrated thresholds.", table_cell)],
        [SafeParagraph("Acceptance Policy (3 Rules)", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("src/acceptance_policy.py: Evaluates Support >= 90%, Contradiction <= 5%, Peak Contradiction Ceiling p < 0.70, and non-zero claim safety check.", table_cell)],
        [SafeParagraph("Targeted Claim Revision Engine", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("src/revision.py: Preserves Entailed claims verbatim; rewrites Neutral/Contradicted claims constrained to retrieved evidence; prunes with REMOVE.", table_cell)],
        [SafeParagraph("FastAPI Web Backend", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("app.py: Exposes /api/summarize_all, /api/summarize, /api/verify, /api/revise, /api/benchmark, /api/samples, /api/health with CORS middleware.", table_cell)],
        [SafeParagraph("React + TypeScript Frontend", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("frontend/src/: 5 interactive pages (Page1Input, Page2Results, Page3Factuality, Page4Compare, Page5Dashboard) compiled with Vite to dist/.", table_cell)],
        [SafeParagraph("500-Sample Benchmark Evaluation", table_cell), SafeParagraph("<b>Implemented & Verified</b>", table_cell), SafeParagraph("data/experiments/exp2_refined_factuality/: Master metrics, CSV logs, language slices, and confusion records for 150 Hindi, 150 English, 200 Hinglish.", table_cell)],
        [SafeParagraph("Full Graph-Based Dependency Resolution", table_cell), SafeParagraph("<b>Partially Implemented</b>", table_cell), SafeParagraph("src/claim_graph.py exists with NetworkX DAG structure; production pipeline uses sequential in-place claim-level revision.", table_cell)],
    ]
    t_audit = Table(audit_data, colWidths=[120, 110, 310])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_audit)
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 2 — COMPLETE PROJECT EXPLANATION & CORE NLP CONCEPTS
    # =========================================================================
    story.append(SafeParagraph("PART 2: Complete Project Explanation & Core NLP Concepts", h1_style))
    story.append(SafeParagraph("<b>1. Text Summarization:</b> The NLP task of taking a longer source document and producing a concise, fluent condensation that retains the essential information.", body_style))
    story.append(SafeParagraph("<b>2. Extractive vs. Abstractive Summarization:</b> Extractive summarization identifies and copies existing sentences verbatim from the source. Abstractive summarization generates new phrasing and syntactic structures using an autoregressive Language Model, similar to human rewriting. However, abstractive summarization creates the risk of factual distortion.", body_style))
    story.append(SafeParagraph("<b>3. Factual Consistency & Hallucination:</b> Factual consistency requires that every proposition asserted in the summary is logically entailed by the source text. A <i>hallucination</i> occurs when the model outputs statements that are either unsupported by (extrinsic hallucination) or directly contradict (intrinsic hallucination) the source.", body_style))
    story.append(SafeParagraph("<b>4. Why LLMs Hallucinate:</b> Modern autoregressive LLMs are trained to maximize the conditional probability of the next token ($P(w_t \\mid w_{<t})$) based on pre-training web statistics. They possess no internal ground-truth verification mechanism. When generating summaries, the model frequently blends pre-training parametric memory (e.g., world knowledge about an entity) with the prompt's source text.", body_style))
    story.append(SafeParagraph("<b>5. Indic & Code-Mixed Challenges:</b> Indic languages like Hindi exhibit rich morphological inflection, variable word order (SOV vs English SVO), and complex post-positions. In code-mixed Hinglish (e.g., <i>'maine Rishabh ko school jane ke liye bola'</i>), English and Hindi words are blended without standard orthography or grammar rules. LLMs frequently misidentify subjects and objects, invert polarity/negation, or invent unmentioned relationships.", body_style))
    
    # Distinction Box
    add_callout(
        "<b>Critical NLP Distinctions:</b><br/>"
        "• <b>Content Preservation:</b> Did the summary retain the essential topic and main points?<br/>"
        "• <b>Meaning Preservation:</b> Did the summary accurately convey the semantics without reversing roles or polarities?<br/>"
        "• <b>Factual Consistency / Faithfulness:</b> Is every single generated claim strictly true according to the source?<br/>"
        "• <b>Fluency & Readability:</b> Does the text sound natural and grammatically correct?<br/>"
        "<i>Why a summary can be fluent but factually wrong:</i> 'Amanda says she will be late' is 100% grammatically fluent, but if the source was about Rishabh going to school, it is completely hallucinated. Conversely, an extractive fragment may be 100% supported but omit 90% of the key context."
    )

    # =========================================================================
    # PART 3 — SYSTEM ARCHITECTURE & WORKFLOW
    # =========================================================================
    story.append(SafeParagraph("PART 3: System Architecture & Real Execution Order", h1_style))
    story.append(SafeParagraph("The system implements a staged, evidence-grounded summarization and verification pipeline. Below is the exact execution flow connecting user input to verified output.", body_style))
    
    arch_flow = [
        [SafeParagraph("Pipeline Stage", table_header), SafeParagraph("Internal Operations", table_header), SafeParagraph("Source File & Function", table_header), SafeParagraph("Output Artifact", table_header)],
        [SafeParagraph("1. User Input & Dispatch", table_cell), SafeParagraph("Receives source text, language (Hindi/Hinglish/English), and length (short/medium/detailed). Dispatches controlled prompt.", table_cell), SafeParagraph("frontend/src/pages/Page1Input.tsx<br/>app.py: /api/summarize_all", table_cell), SafeParagraph("JSON Request Payload with normalized text", table_cell)],
        [SafeParagraph("2. Condition A Generation", table_cell), SafeParagraph("Runs Qwen2.5-1.5B with standard neutral summarization prompt. Generates unconstrained abstractive baseline.", table_cell), SafeParagraph("generate_summaries_local.py:<br/>get_prompts_for_sample()", table_cell), SafeParagraph("Baseline Summary A (57.9 words avg)", table_cell)],
        [SafeParagraph("3. Condition B Generation", table_cell), SafeParagraph("Runs Qwen2.5-1.5B with precision factuality prompt enforcing subject/object binding, negative constraints, and no added causes.", table_cell), SafeParagraph("generate_summaries_local.py:<br/>get_prompts_for_sample()", table_cell), SafeParagraph("Factuality-Aware Summary B (57.6 words avg)", table_cell)],
        [SafeParagraph("4. Atomic Claim Extraction", table_cell), SafeParagraph("Decomposes summary into checkable atomic propositions across terminal punctuation and contrastive conjunctions (while, whereas, जबकि).", table_cell), SafeParagraph("src/claim_extractor.py:<br/>rule_based_claim_split()", table_cell), SafeParagraph("List of Atomic Claims: [C1, C2, ..., Cn]", table_cell)],
        [SafeParagraph("5. Dense Evidence Retrieval", table_cell), SafeParagraph("Segments source document into sentences or speaker turns; computes 384-dim dense embeddings; retrieves top-k evidence via cosine similarity.", table_cell), SafeParagraph("src/evidence_retriever.py:<br/>EvidenceRetriever.retrieve()", table_cell), SafeParagraph("Ranked Evidence Sentences with similarity scores", table_cell)],
        [SafeParagraph("6. Cross-Lingual NLI Verification", table_cell), SafeParagraph("Feeds (Premise: Evidence, Hypothesis: Claim) into mDeBERTa-v3-base-xnli. Applies calibrated thresholds to output probabilities.", table_cell), SafeParagraph("src/nli_verifier.py:<br/>NLIVerifier.verify()", table_cell), SafeParagraph("NLI Labels: Entailment, Contradiction, Neutral + Confidence", table_cell)],
        [SafeParagraph("7. Acceptance Policy Evaluation", table_cell), SafeParagraph("Evaluates 3 gates: Support Rate >= 90%, Contradiction Rate <= 5%, Peak Contradiction Ceiling p < 0.70. Evaluates non-zero claim safety.", table_cell), SafeParagraph("src/acceptance_policy.py:<br/>AcceptancePolicy.evaluate()", table_cell), SafeParagraph("Status: ACCEPTED or REVISE_FLAGGED", table_cell)],
        [SafeParagraph("8. Targeted Revision Loop (Cond C)", table_cell), SafeParagraph("Preserves Entailed claims verbatim. Sends Neutral/Contradicted claims to Qwen for in-place evidence correction or REMOVE pruning.", table_cell), SafeParagraph("src/revision.py:<br/>TargetedReviser.revise_in_place()", table_cell), SafeParagraph("Revised Summary C (46.1 words avg)", table_cell)],
        [SafeParagraph("9. Re-Verification & Audit", table_cell), SafeParagraph("Re-extracts claims from Summary C and re-runs NLI verification to confirm final post-revision support rate and contradiction ceiling.", table_cell), SafeParagraph("app.py: audit_summary_internal()", table_cell), SafeParagraph("Final Verified MultiConditionResult", table_cell)],
    ]
    t_arch = Table(arch_flow, colWidths=[90, 180, 140, 130])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # CONCRETE TRACE EXAMPLE
    story.append(SafeParagraph("<b>Concrete End-to-End Walkthrough Example:</b>", h3_style))
    story.append(SafeParagraph("<b>Input:</b> <i>'maine Rishabh ko school jane ke liye bola'</i> (Hinglish dialogue, 8 words)", body_style))
    story.append(SafeParagraph("• <b>Condition A Output:</b> <i>'Rishabh was told to go to school.'</i> (1 claim: C1='Rishabh was told to go to school.', NLI=Entailment, Support=100%).", body_style))
    story.append(SafeParagraph("• <b>Unconstrained Baseline Failure (Before Fix):</b> Condition B previously generated <i>'Rishabh asked me to go to school with him.'</i> Claim decomposition extracted C1='Rishabh asked me to go to school' and C2='He wanted me to go with him'. Evidence retrieved was <i>'maine Rishabh ko school jane ke liye bola'</i>. mDeBERTa evaluated C1 with $P_{\\text{con}}=0.89$ (Contradiction!) and C2 with $P_{\\text{neu}}=0.92$ (Neutral!). Acceptance policy rejected with status <code>REVISE_HIGH_CONF_CONTRADICTION</code>.", body_style))
    story.append(SafeParagraph("• <b>Condition C Revision:</b> Reviser preserved 0 claims, rewrote C1 against source evidence to <i>'Rishabh was instructed to go to school'</i>, and pruned C2 (REMOVE). Final Condition C achieved 100% Support Rate and 0% Contradiction Rate.", body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 4 — INDIVIDUAL TEAM MEMBER PREPARATION
    # =========================================================================
    story.append(SafeParagraph("PART 4: Individual Team Member Technical Deep-Dives", h1_style))

    # MEMBER 1: RISHIKA
    story.append(SafeParagraph("Member 1 — Rishika: Dataset Curation & NLP Preprocessing", h2_style))
    story.append(SafeParagraph("<b>Core Role:</b> Sourcing, cleaning, standardizing, and constructing the 500-sample multilingual evaluation benchmark spanning Hindi, Hinglish, and English.", body_style))
    story.append(SafeParagraph("<b>1. Datasets Used:</b>", h3_style))
    story.append(SafeParagraph("• <b>ILSUM 2.0 (Indian Language Summarization):</b> Sourced from Hindi news portals (Dainik Jagran, Navbharat Times) and English national news. Contains formal news articles paired with human-written extractive/abstractive lead paragraphs.", bullet_style))
    story.append(SafeParagraph("• <b>GupShup:</b> First public Hinglish-to-English conversation summarization dataset. Consists of informal WhatsApp/SMS style multi-turn dialogues in Romanized Hindi-English, paired with standard English reference summaries.", bullet_style))
    story.append(SafeParagraph("<b>2. Dataset Statistics & Splits:</b> Total Pool = 500 candidate samples (150 Hindi, 150 English, 200 Hinglish dialogues). Formatted into <code>candidates_master.csv</code> with fields: <code>sample_id, language, split, source_text, reference_summary, source_words</code>.", body_style))
    story.append(SafeParagraph("<b>3. Preprocessing Operations Applied:</b>", h3_style))
    story.append(SafeParagraph("• <i>Unicode Normalization:</i> Stripped extraneous formatting, fixed Devanagari ZWJ/ZWNJ artifacts, and unified Hindi punctuation (Devanagari danda '।' vs latin full-stop '.').", bullet_style))
    story.append(SafeParagraph("• <i>Dialogue Turn Segmentation:</i> Parsed multi-turn conversational transcripts using regex patterns matching speaker turns (e.g., <code>Amanda: ... Jerry: ...</code>) to preserve conversational context for retrieval.", bullet_style))
    story.append(SafeParagraph("• <i>Deduplication & Missing Data Handling:</i> Pruned null entries, stripped leading/trailing whitespace, and filtered degenerate inputs (< 5 words).", bullet_style))
    
    # Rishika Viva
    story.append(SafeParagraph("<b>Top Viva Questions & Answers for Rishika:</b>", h3_style))
    story.append(SafeParagraph("<b>Q1: Why did you choose GupShup instead of standard English dialogue datasets like SAMSum?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> SAMSum is strictly monolingual English. GupShup provides real code-mixed Hindi-English (Hinglish) conversational text in Roman script. Our core research objective is evaluating factuality in Indic and code-mixed settings where models suffer from high hallucination rates.", a_style))
    story.append(SafeParagraph("<b>Q2: How do you handle Hindi in Roman script versus Devanagari script?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> Devanagari Hindi is retained in native script and evaluated against Devanagari references. Romanized Hinglish is treated as a Hinglish-to-English translation-summarization task: the source is Romanized code-mixed text, while the target summary is standard English, matching GupShup benchmark protocols.", a_style))
    story.append(Spacer(1, 10))

    # MEMBER 2: SIMRAN
    story.append(SafeParagraph("Member 2 — Simran: Summarization Model & Prompt Engineering", h2_style))
    story.append(SafeParagraph("<b>Core Role:</b> Model selection, prompt architecture design, generation parameter tuning, and local execution on Apple Silicon MPS hardware.", body_style))
    story.append(SafeParagraph("<b>1. Model Selection — Qwen2.5-1.5B-Instruct:</b>", h3_style))
    story.append(SafeParagraph("• Developed by Alibaba Cloud, Qwen2.5 is an autoregressive decoder-only Transformer with strong multilingual pre-training across Asian and Indic languages.", bullet_style))
    story.append(SafeParagraph("• The 1.5B parameter variant was selected because it balances high multilingual zero-shot instruction-following with the ability to run 100% locally on Apple Silicon MPS without cloud API costs or latency bottlenecks.", bullet_style))
    story.append(SafeParagraph("<b>2. Condition A vs. Condition B Prompt Architecture:</b>", h3_style))
    story.append(SafeParagraph("• <b>Condition A (Standard Baseline):</b> Uses an unconstrained prompt instructing the model to provide a concise summary retaining general meaning. It contains no negative constraints.", bullet_style))
    story.append(SafeParagraph("• <b>Condition B (Factuality-Aware Precision Prompt):</b> Enforces strict negative constraints: (1) Do not add external knowledge or unmentioned context, (2) Preserve exact subject-action-object relations (who told whom), (3) Never infer causation or intentions, (4) Preserve negation (nahi/mat), dates, and numbers, (5) Do not expand 1-sentence inputs into multiple sentences.", bullet_style))
    story.append(SafeParagraph("<b>3. Inference Hyperparameters:</b> <code>temperature=0.2</code> (low temperature to discourage creative hallucinations), <code>do_sample=False</code> or greedy decoding, and length budgets: Short (150-220 tokens), Medium (260-300 tokens), Detailed (450 tokens).", body_style))
    
    # Simran Viva
    story.append(SafeParagraph("<b>Top Viva Questions & Answers for Simran:</b>", h3_style))
    story.append(SafeParagraph("<b>Q1: Why does Condition B prompting alone not completely eliminate hallucinations?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> Prompting operates at the input level, but autoregressive generation remains probabilistic. On out-of-distribution code-mixed syntax, the model's parametric priors still trigger explicative hallucinations (e.g., adding inferred causes like 'due to limited study hours'). This proves why external verification (Condition C) is scientifically necessary.", a_style))
    story.append(SafeParagraph("<b>Q2: What does the 'Instruct' suffix mean in Qwen2.5-1.5B-Instruct?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> The base model is pre-trained purely on next-token prediction on raw text. The Instruct variant has undergone Supervised Fine-Tuning (SFT) and RLHF/DPO on instruction-following datasets, allowing it to adhere to complex formatting directives and system prompts.", a_style))
    story.append(Spacer(1, 10))

    # MEMBER 3: AARUSHI
    story.append(SafeParagraph("Member 3 — Aarushi: Factuality Verification & Targeted Revision", h2_style))
    story.append(SafeParagraph("<b>Core Role:</b> Implementing the complete Phase 4 & Phase 5 automated verification and revision engine: claim extraction, dense evidence retrieval, multilingual NLI classification, 3-rule acceptance policy, and in-place revision.", body_style))
    story.append(SafeParagraph("<b>1. Atomic Claim Extraction (<code>src/claim_extractor.py</code>):</b>", h3_style))
    story.append(SafeParagraph("• Deconstructs summary text into single-fact propositions using <code>rule_based_claim_split()</code>.", bullet_style))
    story.append(SafeParagraph("• Splits across terminal punctuation (<code>. ! ? । \\n ; —</code>) and decomposes compound contrastive clauses using regex lookbehinds: <code>r'(?<=,)\\s+(?:while|whereas|जबकि|परन्तु)\\s+'</code>.", bullet_style))
    story.append(SafeParagraph("• Filters malformed sentence fragments (prunes propositions with < 3 words or < 10 characters).", bullet_style))
    story.append(SafeParagraph("<b>2. Multilingual Evidence Retrieval (<code>src/evidence_retriever.py</code>):</b>", h3_style))
    story.append(SafeParagraph("• Model: <code>sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2</code> (384-dimensional dense semantic space).", bullet_style))
    story.append(SafeParagraph("• Segments source into evidence units (news sentences or speaker utterances). Encodes claim and source units, computing Cosine Similarity: $$\\text{sim}(u, v) = \\frac{u \\cdot v}{\\|u\\| \\|v\\|}$$. Retrieves Top-$k=5$ most relevant source candidates.", bullet_style))
    story.append(SafeParagraph("<b>3. Cross-Lingual NLI Verification (<code>src/nli_verifier.py</code>):</b>", h3_style))
    story.append(SafeParagraph("• Model: <code>MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7</code>.", bullet_style))
    story.append(SafeParagraph("• Compares Premise (Retrieved Source Evidence) against Hypothesis (Extracted Claim).", bullet_style))
    story.append(SafeParagraph("• <i>Calibrated Decision Rules:</i> Contradiction if $P_{\\text{con}} \\ge 0.45$ or ($P_{\\text{con}} > P_{\\text{ent}}$ and $P_{\\text{con}} \\ge 0.35$). Strict Entailment if $P_{\\text{ent}} \\ge 0.65$ and $P_{\\text{ent}} > P_{\\text{neu}} + 0.10$. Otherwise Neutral.", bullet_style))
    story.append(SafeParagraph("<b>4. Automated Acceptance Policy (<code>src/acceptance_policy.py</code>):</b>", h3_style))
    story.append(SafeParagraph("• Gate 1: $\\text{Support Rate} = \\frac{|\\text{Entailments}|}{|\\text{Total Claims}|} \\times 100 \\ge 90.0\\%$.", bullet_style))
    story.append(SafeParagraph("• Gate 2: $\\text{Contradiction Rate} = \\frac{|\\text{Contradictions}|}{|\\text{Total Claims}|} \\times 100 \\le 5.0\\%$.", bullet_style))
    story.append(SafeParagraph("• Gate 3: Peak Contradiction Ceiling: $p = \\max_i P_{\\text{con}}(c_i) < 0.70$ (no individual high-confidence contradiction).", bullet_style))
    story.append(SafeParagraph("• Zero-Claim Safeguard: Summaries yielding zero claims are rejected as undefined.", bullet_style))
    story.append(SafeParagraph("<b>5. Targeted In-Place Revision (<code>src/revision.py</code>):</b>", h3_style))
    story.append(SafeParagraph("• Entailed claims are preserved verbatim (no unnecessary re-generation).", bullet_style))
    story.append(SafeParagraph("• Contradicted/Neutral claims are sent to Qwen with source and evidence context. If ungroundable, Qwen returns <code>REMOVE</code> and the claim is surgically pruned.", bullet_style))

    # Aarushi Viva
    story.append(SafeParagraph("<b>Top Viva Questions & Answers for Aarushi:</b>", h3_style))
    story.append(SafeParagraph("<b>Q1: Why do you retrieve evidence using Sentence-Transformers before calling NLI, instead of passing the entire source document as premise?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> mDeBERTa has a 512-token context limit and suffers from 'needle-in-a-haystack' distraction when processing long premises. Retrieving top-k dense semantic units isolates the specific factual anchor, dramatically increasing NLI classification precision.", a_style))
    story.append(SafeParagraph("<b>Q2: What does a Neutral NLI prediction mean, and why is it not classified as Entailment?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> Neutral means the claim is neither confirmed nor refuted by the source. In summarization, unmentioned facts represent hallucinations (extrinsic hallucinations). Treating Neutral as Entailment would allow unsupported statements to pass verification.", a_style))
    story.append(Spacer(1, 10))

    # MEMBER 4: KHANAK
    story.append(SafeParagraph("Member 4 — Khanak: Evaluation & Research Benchmark Analysis", h2_style))
    story.append(SafeParagraph("<b>Core Role:</b> Designing the experimental protocol, running the 500-sample benchmark, computing ROUGE lexical overlap vs. NLI factuality metrics, and analyzing language-specific failure modes.", body_style))
    story.append(SafeParagraph("<b>1. Comprehensive Benchmark Results (N = 500 Samples):</b>", h3_style))
    
    bench_data = [
        [SafeParagraph("Metric", table_header), SafeParagraph("Condition A (Standard)", table_header), SafeParagraph("Condition B (Factuality)", table_header), SafeParagraph("Condition C (Revision Loop)", table_header), SafeParagraph("Net Delta (C vs. A)", table_header)],
        [SafeParagraph("ROUGE-1 Precision", table_cell), SafeParagraph("0.2552", table_cell), SafeParagraph("0.2635", table_cell), SafeParagraph("<b>0.2862</b>", table_cell), SafeParagraph("+0.0310 (+12.1%)", table_cell)],
        [SafeParagraph("ROUGE-1 Recall", table_cell), SafeParagraph("0.4737", table_cell), SafeParagraph("0.4845", table_cell), SafeParagraph("0.3995", table_cell), SafeParagraph("-0.0742 (-15.6%)", table_cell)],
        [SafeParagraph("ROUGE-1 F1-Score", table_cell), SafeParagraph("0.3170", table_cell), SafeParagraph("0.3250", table_cell), SafeParagraph("0.2999", table_cell), SafeParagraph("-0.0171", table_cell)],
        [SafeParagraph("Average Summary Length", table_cell), SafeParagraph("57.9 words", table_cell), SafeParagraph("57.6 words", table_cell), SafeParagraph("46.1 words", table_cell), SafeParagraph("-11.8 words (concise)", table_cell)],
        [SafeParagraph("Compression Ratio (%)", table_cell), SafeParagraph("35.45%", table_cell), SafeParagraph("35.80%", table_cell), SafeParagraph("27.63%", table_cell), SafeParagraph("-7.82%", table_cell)],
        [SafeParagraph("Inference Time (s)", table_cell), SafeParagraph("7.69s", table_cell), SafeParagraph("8.30s", table_cell), SafeParagraph("13.95s", table_cell), SafeParagraph("+6.26s (verification overhead)", table_cell)],
        [SafeParagraph("Macro Factual Support (%)", table_cell), SafeParagraph("62.30%", table_cell), SafeParagraph("61.86%", table_cell), SafeParagraph("<b>81.40%</b>", table_cell), SafeParagraph("<b>+19.10%</b>", table_cell)],
        [SafeParagraph("Macro Contradiction (%)", table_cell), SafeParagraph("11.66%", table_cell), SafeParagraph("11.00%", table_cell), SafeParagraph("<b>4.83%</b>", table_cell), SafeParagraph("<b>-6.83%</b>", table_cell)],
        [SafeParagraph("Micro Support (Claims)", table_cell), SafeParagraph("1296/2012 (64.41%)", table_cell), SafeParagraph("1161/1869 (62.12%)", table_cell), SafeParagraph("<b>1220/1486 (82.10%)</b>", table_cell), SafeParagraph("<b>+17.69%</b>", table_cell)],
        [SafeParagraph("Micro Contradiction (Claims)", table_cell), SafeParagraph("228/2012 (11.33%)", table_cell), SafeParagraph("218/1869 (11.66%)", table_cell), SafeParagraph("<b>69/1486 (4.64%)</b>", table_cell), SafeParagraph("<b>-6.69%</b>", table_cell)],
        [SafeParagraph("Strict Policy Acceptance (%)", table_cell), SafeParagraph("23.60% (118/500)", table_cell), SafeParagraph("24.60% (123/500)", table_cell), SafeParagraph("<b>62.60% (313/500)</b>", table_cell), SafeParagraph("<b>+39.00%</b>", table_cell)],
    ]
    t_bench = Table(bench_data, colWidths=[130, 95, 100, 110, 105])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 8))

    # Khanak Viva
    story.append(SafeParagraph("<b>Top Viva Questions & Answers for Khanak:</b>", h3_style))
    story.append(SafeParagraph("<b>Q1: Why did ROUGE Recall drop in Condition C (0.3995 vs 0.4737 in A) while Factual Support increased (+19.1%)?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> This is the classic <i>Recall-Precision Trade-off</i> in factual summarization. Condition C actively prunes ungrounded statements (reducing summary length from 57.9 to 46.1 words). Because hallucinated tokens are removed, n-gram recall against reference summaries slightly decreases, but Precision increases from 0.2552 to 0.2862 and Factual Support surges from 62.3% to 81.4%.", a_style))
    story.append(SafeParagraph("<b>Q2: What is the difference between Macro-average and Micro-average in your evaluation?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> Macro-average evaluates support rate per document and averages across all 500 documents, giving equal weight to short and long documents. Micro-average pools all individual claims (e.g., N=1486 claims in C) and calculates the exact global proportion of supported claims.", a_style))
    story.append(Spacer(1, 10))

    # MEMBER 5: HINA
    story.append(SafeParagraph("Member 5 — Hina: Frontend, Backend Integration & Deployment", h2_style))
    story.append(SafeParagraph("<b>Core Role:</b> Developing the responsive React 18 / TypeScript frontend, building the FastAPI REST backend, orchestrating multi-condition asynchronous execution, and managing local deployment.", body_style))
    story.append(SafeParagraph("<b>1. Architecture & API Contracts:</b>", h3_style))
    story.append(SafeParagraph("• <b>Frontend:</b> Single Page Application (SPA) built with React 18, TypeScript, Tailwind CSS, and Lucide-react. Five dedicated views: (1) Input, (2) Results, (3) Factuality Report, (4) Comparison, (5) Benchmark Dashboard.", bullet_style))
    story.append(SafeParagraph("• <b>FastAPI Backend (<code>app.py</code>):</b> High-performance Python ASGI backend. Endpoints:", bullet_style))
    story.append(SafeParagraph("  - <code>POST /api/summarize_all</code>: Receives source document, language, and length; runs Conditions A, B, and C in one unified call and returns verified JSON payload.", code_style))
    story.append(SafeParagraph("  - <code>POST /api/verify</code>: Extracts claims and audits any arbitrary summary text.", code_style))
    story.append(SafeParagraph("  - <code>POST /api/revise</code>: Triggers in-place revision loop on problematic claims.", code_style))
    story.append(SafeParagraph("  - <code>GET /api/benchmark</code>: Streams pre-computed 500-sample benchmark metrics.", code_style))
    story.append(SafeParagraph("• <b>Deployment:</b> Local deployment managed via <code>./run_ui.sh</code> using Uvicorn on <code>http://0.0.0.0:8000</code> with static file mounting of the compiled Vite <code>dist/</code> assets.", bullet_style))

    # Hina Viva
    story.append(SafeParagraph("<b>Top Viva Questions & Answers for Hina:</b>", h3_style))
    story.append(SafeParagraph("<b>Q1: How do you prevent frontend timeouts given that running 3 conditions with NLI takes 10-15 seconds?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> FastAPI utilizes asynchronous request handlers and PyTorch MPS inference. On the frontend, React maintains an explicit loading state (<code>loadingGenerate</code>) with visual step-by-step progress indicators, preventing race conditions or duplicate submissions.", a_style))
    story.append(SafeParagraph("<b>Q2: What was the Amanda cookies bug shown in early screenshots, and how did you resolve it?</b>", q_style))
    story.append(SafeParagraph("<i>Answer:</i> The earlier client prototype had a fallback to static mock sample GUP_001 whenever an API error occurred. We completely eliminated all mock fallbacks in <code>frontend/src/api.ts</code> and wired the interface directly to the live backend, ensuring typed text is always passed to the ML pipeline.", a_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 5 — END-TO-END LIVE DEMONSTRATION SCRIPT
    # =========================================================================
    story.append(SafeParagraph("PART 5: End-to-End Live Demonstration Script", h1_style))
    story.append(SafeParagraph("During the evaluation, the team will run a live interactive demonstration. Follow this exact 5-step sequence:", body_style))
    story.append(SafeParagraph("<b>Step 1 — Input Submission (Page 1):</b><br/>1. Open <code>http://localhost:8000</code>.<br/>2. Select Language: <b>Hinglish</b>.<br/>3. Paste test document: <i>'maine Rishabh ko school jane ke liye bola'</i>.<br/>4. Select Length: <b>Medium</b>.<br/>5. Click <b>Generate All Summaries</b> button.", body_style))
    story.append(SafeParagraph("<b>Step 2 — Inspecting Summaries Side-by-Side (Page 2):</b><br/>Show that all 3 conditions generated summaries from the same source text:<br/>• Condition A (Standard): <i>'Rishabh was told to go to school.'</i><br/>• Condition B (Factuality-Aware): <i>'Rishabh was instructed to go to school.'</i><br/>• Condition C (Verified): <i>'Rishabh was instructed to go to school.'</i> (100% Support, 0% Contradiction).", body_style))
    story.append(SafeParagraph("<b>Step 3 — Inspecting Claim-Level Verification (Page 3):</b><br/>Click <b>Audit Claims</b> on Condition B. Show the faculty the atomic breakdown:<br/>• Claim C1: <i>'Rishabh was instructed to go to school.'</i><br/>• Evidence Retrieved: <i>'maine Rishabh ko school jane ke liye bola'</i> (Cosine Sim: 0.88).<br/>• NLI Probabilities: Entailment=0.9072, Neutral=0.0897, Contradiction=0.0030.<br/>• Status: <b>ACCEPTED (Green Pill)</b>.", body_style))
    story.append(SafeParagraph("<b>Step 4 — Demonstrating Targeted Revision (Page 4):</b><br/>Demonstrate a case where Condition B hallucinated an ungrounded cause (e.g., college time management test). Show how Condition C detects the contradiction, triggers in-place revision, and prunes ungrounded clauses.", body_style))
    story.append(SafeParagraph("<b>Step 5 — Benchmark Metrics Dashboard (Page 5):</b><br/>Show the interactive 500-sample benchmark dashboard displaying the macro support gain (+19.1%) and contradiction reduction (-6.8%).", body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 6 — TECHNICAL COMPARISON OF CONDITIONS A, B, AND C
    # =========================================================================
    story.append(SafeParagraph("PART 6: Technical Comparison of Conditions A, B, and C", h1_style))
    
    cond_comp = [
        [SafeParagraph("Dimension", table_header), SafeParagraph("Condition A: Standard", table_header), SafeParagraph("Condition B: Factuality-Aware", table_header), SafeParagraph("Condition C: Revision Loop", table_header)],
        [SafeParagraph("Core Mechanism", table_cell), SafeParagraph("Zero-shot neutral prompting", table_cell), SafeParagraph("Prompting with negative constraints & role binding", table_cell), SafeParagraph("Iterative NLI claim verification & surgical revision", table_cell)],
        [SafeParagraph("Factual Support Rate", table_cell), SafeParagraph("62.30% Macro / 64.41% Micro", table_cell), SafeParagraph("61.86% Macro / 62.12% Micro", table_cell), SafeParagraph("<b>81.40% Macro / 82.10% Micro (+19.1%)</b>", table_cell)],
        [SafeParagraph("Contradiction Rate", table_cell), SafeParagraph("11.66% Macro / 11.33% Micro", table_cell), SafeParagraph("11.00% Macro / 11.66% Micro", table_cell), SafeParagraph("<b>4.83% Macro / 4.64% Micro (-6.8%)</b>", table_cell)],
        [SafeParagraph("Policy Acceptance Rate", table_cell), SafeParagraph("23.60% (118/500)", table_cell), SafeParagraph("24.60% (123/500)", table_cell), SafeParagraph("<b>62.60% (313/500) (+39.0%)</b>", table_cell)],
        [SafeParagraph("Summary Length (Words)", table_cell), SafeParagraph("57.9 words", table_cell), SafeParagraph("57.6 words", table_cell), SafeParagraph("46.1 words (concise, pruned)", table_cell)],
        [SafeParagraph("Inference Latency", table_cell), SafeParagraph("7.69s (Single LLM pass)", table_cell), SafeParagraph("8.30s (Single LLM pass)", table_cell), SafeParagraph("13.95s (Generation + Retrieval + NLI + Revision)", table_cell)],
        [SafeParagraph("Primary Weakness", table_cell), SafeParagraph("High hallucination rate, role inversions on Hinglish", table_cell), SafeParagraph("Cannot prevent ungrounded inferences on subtle syntax", table_cell), SafeParagraph("Higher latency overhead; slight drop in ROUGE recall", table_cell)],
    ]
    t_comp = Table(cond_comp, colWidths=[100, 140, 150, 150])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 7 — COMPLETE TECH STACK MATRIX
    # =========================================================================
    story.append(SafeParagraph("PART 7: Complete Tech Stack Matrix", h1_style))
    
    stack_data = [
        [SafeParagraph("Technology", table_header), SafeParagraph("Exact Version / Model", table_header), SafeParagraph("Role in FactIndic", table_header), SafeParagraph("Why Selected vs. Alternatives", table_header)],
        [SafeParagraph("Generation LLM", table_cell), SafeParagraph("Qwen/Qwen2.5-1.5B-Instruct", table_cell), SafeParagraph("Generates summaries for Cond A, B, and revisions in C", table_cell), SafeParagraph("Top-tier multilingual zero-shot capabilities; lightweight enough to run locally on Apple Silicon MPS without cloud cost.", table_cell)],
        [SafeParagraph("NLI Classifier", table_cell), SafeParagraph("mDeBERTa-v3-base-xnli", table_cell), SafeParagraph("Predicts Entailment, Contradiction, Neutral probabilities", table_cell), SafeParagraph("Trained on XNLI across 15+ languages including Hindi; superior cross-lingual semantic alignment compared to monolingual BERT.", table_cell)],
        [SafeParagraph("Evidence Retriever", table_cell), SafeParagraph("paraphrase-multilingual-MiniLM-L12-v2", table_cell), SafeParagraph("Dense sentence embedding for Top-k evidence retrieval", table_cell), SafeParagraph("Produces 384-dim dense vectors; highly efficient cosine similarity computation over multilingual source documents.", table_cell)],
        [SafeParagraph("Deep Learning", table_cell), SafeParagraph("PyTorch 2.2.0 + Transformers 4.40.0", table_cell), SafeParagraph("Model execution, tensor management, tokenization", table_cell), SafeParagraph("Standard industry frameworks with native Apple Silicon Metal Performance Shaders (MPS) GPU acceleration.", table_cell)],
        [SafeParagraph("Web Backend", table_cell), SafeParagraph("FastAPI 0.110.0 + Uvicorn 0.29.0", table_cell), SafeParagraph("Asynchronous REST API server", table_cell), SafeParagraph("High throughput, automatic OpenAPI documentation, clean async integration with PyTorch inference pipelines.", table_cell)],
        [SafeParagraph("Web Frontend", table_cell), SafeParagraph("React 18 + TypeScript + Vite", table_cell), SafeParagraph("Interactive 5-page research UI", table_cell), SafeParagraph("Type-safe state management, fast Vite hot-module replacement, Tailwind CSS for dark scientific dashboard styling.", table_cell)],
        [SafeParagraph("Evaluation Tools", table_cell), SafeParagraph("evaluate (ROUGE) + scikit-learn", table_cell), SafeParagraph("ROUGE-1/2/L overlap and confusion matrix calculation", table_cell), SafeParagraph("Standardized academic evaluation metrics for NLP summarization benchmarks.", table_cell)],
    ]
    t_stack = Table(stack_data, colWidths=[90, 130, 140, 180])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 8 — COMPREHENSIVE TEAM VIVA QUESTION BANK (110 QUESTIONS)
    # =========================================================================
    story.append(SafeParagraph("PART 8: Comprehensive Team-Wide Viva Question Bank", h1_style))
    story.append(SafeParagraph("Categorized into 5 distinct difficulty tiers: Basic (20), Intermediate (30), Advanced (30), Cross-Member (15), and Faculty Follow-ups (15).", body_style))

    # SECTION A: BASIC QUESTIONS
    story.append(SafeParagraph("A. Basic Project Questions (Q1 – Q20)", h2_style))
    basic_qa = [
        ("1. What is the primary objective of Project FactIndic?", "To detect, verify, and surgically correct factual hallucinations in abstractive text summaries of Indic (Hindi), English, and code-mixed (Hinglish) text using an automated NLI verification and targeted revision pipeline."),
        ("2. What are the three experimental conditions evaluated?", "Condition A (Standard baseline summarization), Condition B (Factuality-aware constrained prompting), and Condition C (Automated NLI-guided targeted claim revision)."),
        ("3. Why is abstractive summarization prone to hallucinations?", "Because autoregressive LLMs generate text based on probabilistic next-token predictions from pre-training web statistics rather than verifying claims against the provided source document."),
        ("4. What is the difference between an intrinsic and extrinsic hallucination?", "An intrinsic hallucination directly contradicts facts present in the source text. An extrinsic hallucination introduces external ungrounded facts that were never mentioned in the source."),
        ("5. What is Hinglish?", "A hybrid code-mixed linguistic variety blending Hindi vocabulary and syntax with English words, commonly written in informal Roman script on digital communication platforms."),
        ("6. Which dataset was used for Hindi news summarization?", "ILSUM 2.0 (Indian Language Summarization), containing formal Hindi articles from news portals paired with reference summaries."),
        ("7. Which dataset was used for code-mixed dialogue summarization?", "GupShup, a conversational Hinglish dataset consisting of multi-turn Romanized dialogues paired with English reference summaries."),
        ("8. How many samples were evaluated in the final benchmark?", "500 balanced samples: 150 Hindi news articles, 150 English news articles, and 200 Hinglish conversations."),
        ("9. Which primary generative LLM is used in FactIndic?", "Qwen/Qwen2.5-1.5B-Instruct, running locally on Apple Silicon MPS hardware."),
        ("10. Which model is used for Natural Language Inference (NLI)?", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7."),
        ("11. Which model is used for evidence retrieval?", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, mapping sentences into 384-dimensional dense vectors."),
        ("12. What are the three classes predicted by the NLI verifier?", "Entailment (source supports the claim), Contradiction (source refutes the claim), and Neutral (source neither supports nor refutes the claim)."),
        ("13. What is an atomic claim?", "A deconstructed, self-contained proposition expressing exactly one factual assertion (an entity, action, date, number, or relation) that can be checked independently."),
        ("14. What are the 3 criteria of the automated Acceptance Policy?", "Support Rate >= 90%, Contradiction Rate <= 5%, and Peak Contradiction Ceiling p < 0.70."),
        ("15. Why does high fluency not guarantee factual correctness?", "Language models easily generate grammatically flawless and articulate sentences that describe events or assertions completely fabricated out of pre-training memory."),
        ("16. What is ROUGE?", "Recall-Oriented Understudy for Gisting Evaluation, measuring n-gram lexical overlap between generated summaries and ground-truth human reference summaries."),
        ("17. What technology powers the web backend?", "FastAPI running with Uvicorn ASGI server in Python 3.11."),
        ("18. What technology powers the web frontend?", "React 18 with TypeScript, Vite bundler, and Tailwind CSS."),
        ("19. What is Apple Silicon MPS?", "Metal Performance Shaders, Apple's GPU acceleration framework enabling fast local PyTorch tensor operations on M-series chips."),
        ("20. What is the main finding of Condition C compared to Condition A?", "Condition C increased macro factual support by +19.1% (surging to 81.4%) and reduced contradiction rates by -6.8% (dropping to 4.83%)."),
    ]
    for q, a in basic_qa:
        story.append(SafeParagraph(f"<b>Q{q}</b>", q_style))
        story.append(SafeParagraph(f"<b>A:</b> {a}", a_style))

    # SECTION B: INTERMEDIATE QUESTIONS
    story.append(SafeParagraph("B. Intermediate Technical Questions (Q21 – Q50)", h2_style))
    inter_qa = [
        ("21. How does rule_based_claim_split extract atomic claims?", "It splits text across sentence boundaries (.!?।\\n;—) and decomposes compound contrastive clauses using regex matching subordinators like 'while', 'whereas', and 'जबकि'."),
        ("22. Why are claims with fewer than 3 words or 10 characters filtered out?", "To prevent punctuation fragments, quotation artifacts, or incomplete tokens from polluting the NLI verification pipeline."),
        ("23. How does dense evidence retrieval compute similarity scores?", "It encodes the claim and each source sentence using MiniLM-L12 embeddings and computes the dot product of their L2-normalized vectors (Cosine Similarity)."),
        ("24. Why is top-k=5 evidence retrieval used instead of passing the entire source to NLI?", "DeBERTa has a 512-token limit, and passing large documents causes attention dilution. Top-k dense retrieval isolates the specific factual evidence sentence."),
        ("25. How are speaker turns segmented in dialogue documents?", "Using regex patterns matching conversational transcripts (e.g., 'Speaker: utterance' or line breaks) so that individual conversational utterances serve as evidence units."),
        ("26. What are the calibrated NLI decision thresholds in src/nli_verifier.py?", "Contradiction if p_con >= 0.45 or (p_con > p_ent and p_con >= 0.35); Entailment if p_ent >= 0.65 and p_ent > p_neu + 0.10; otherwise Neutral."),
        ("27. Why is a probability threshold of 0.45 used for contradiction instead of 0.50?", "In factual verification, missing a contradiction (false negative) is catastrophic. A slightly more sensitive threshold safely catches distorted claims."),
        ("28. What does Peak Contradiction Ceiling p < 0.70 enforce?", "It guarantees that even if a summary has an overall 90% support rate, it is rejected if even a single claim has a severe contradiction probability >= 0.70."),
        ("29. What happens when zero claims are extracted from a summary?", "src/acceptance_policy.py catches this edge case and explicitly rejects the summary with status REVISE_ZERO_CLAIMS."),
        ("30. In Condition C revision, what happens to Entailed claims?", "Entailed claims are preserved verbatim to maintain stability and prevent unnecessary re-generation of already verified facts."),
        ("31. In Condition C revision, what happens to Neutral and Contradicted claims?", "They are passed to Qwen with source evidence to be rewritten concisely; if unsupported, the model outputs REMOVE and the claim is pruned."),
        ("32. Why does Condition C improve ROUGE Precision while Recall decreases?", "Condition C prunes ungrounded clauses. Shorter, strictly factual summaries have fewer false-positive tokens (higher precision), but cover fewer reference n-grams (lower recall)."),
        ("33. What is the compression ratio formula used in FactIndic?", "Compression Ratio (%) = (Summary Word Count / Source Word Count) * 100."),
        ("34. Why is temperature set to 0.2 during summarization?", "Low temperature sharpens the softmax distribution over logits, prioritizing high-probability factual tokens over exploratory/creative generation."),
        ("35. What is the role of get_prompts_for_sample in generate_summaries_local.py?", "It constructs language-adaptive prompts for Hindi, Hinglish, and English, enforcing script preservation (Devanagari for Hindi, English for Hinglish)."),
        ("36. How does Condition B handle Hinglish dialogue summarization?", "It explicitly directs the model to summarize the Romanized dialogue into standard English while strictly preserving subject and object roles (who told whom)."),
        ("37. Why did the college time-management test previously reverse meaning?", "The model misinterpreted the Hindi purpose clause 'taaki important tasks miss na ho' as a failure outcome ('frequently overlook tasks')."),
        ("38. How was the meaning reversal issue resolved in the Condition B prompt?", "By adding strict instructions: 'Never convert an intention or purpose into a failure outcome' and enforcing subject-action preservation."),
        ("39. What is the purpose of app.py /api/summarize_all?", "It receives a source document and runs Condition A, Condition B, and Condition C in a unified pipeline, returning full comparative metrics in one response."),
        ("40. What is CORS and why is it configured in app.py?", "Cross-Origin Resource Sharing. CORSMiddleware allows the React frontend on localhost:5173 to communicate with the FastAPI backend on localhost:8000."),
        ("41. How does the frontend handle loading states during 10-15s inference?", "React sets loadingGenerate=true, disabling buttons and displaying an animated spinner with pipeline status text."),
        ("42. What information does Page 3 Factuality Report display?", "Each atomic claim, its NLI label, softmax probability distribution, retrieved source evidence sentence, and explanation badge."),
        ("43. What information does Page 4 Compare display?", "A side-by-side comparison of Condition A, B, and C summaries with word count, compression ratio, support rate, and contradiction delta."),
        ("44. What information does Page 5 Dashboard display?", "Macro and micro benchmark metrics across all 500 samples, including language slice breakdowns for Hindi, Hinglish, and English."),
        ("45. Why does Hindi achieve higher support rates (92.98%) than English (75.45%)?", "ILSUM Hindi news articles have high lead bias and formal journalistic structure, making facts easier for mDeBERTa to ground than conversational English."),
        ("46. Why does Hinglish exhibit the highest compression ratio (50.4%)?", "Hinglish dialogues are often short and informal (e.g., 20-30 words); converting them into a complete English sentence naturally yields a higher ratio."),
        ("47. What is an autoregressive decoder-only architecture?", "A Transformer architecture (like Qwen) where each token attends only to previous tokens and generates text sequentially from left to right."),
        ("48. What is cross-attention versus self-attention?", "Self-attention computes representations within the same sequence. Cross-attention attends across two different sequences (e.g., decoder attending to encoder outputs)."),
        ("49. What is SentencePiece tokenization?", "A subword tokenization algorithm that treats text as a raw stream of characters, handling whitespace and multilingual scripts without language-specific segmenters."),
        ("50. How does mDeBERTa-v3 differ from standard BERT?", "It uses Disentangled Attention (representing content and relative position vectors separately) and was trained with Replaced Token Detection (ELECTRA-style)."),
    ]
    for q, a in inter_qa:
        story.append(SafeParagraph(f"<b>Q{q}</b>", q_style))
        story.append(SafeParagraph(f"<b>A:</b> {a}", a_style))

    # SECTION C: ADVANCED QUESTIONS
    story.append(SafeParagraph("C. Advanced Technical Questions (Q51 – Q80)", h2_style))
    adv_qa = [
        ("51. What is the mathematical definition of Softmax in NLI classification?", "Softmax converts raw logits $z_i$ into probabilities: $$P(y=k \\mid x) = \\frac{e^{z_k}}{\\sum_{j=1}^C e^{z_j}}$$ where $C \\in \\{\\text{entailment, neutral, contradiction}\\}$."),
        ("52. How is Macro Factual Support Rate calculated across a corpus?", "$$\\text{Macro Support} = \\frac{1}{N} \\sum_{d=1}^N \\left( \\frac{|\\text{Entailments}_d|}{|\\text{Claims}_d|} \\times 100 \\right)$$."),
        ("53. How is Micro Factual Support Rate calculated across a corpus?", "$$\\text{Micro Support} = \\frac{\\sum_{d=1}^N |\\text{Entailments}_d|}{\\sum_{d=1}^N |\\text{Claims}_d|} \\times 100$$."),
        ("54. Why does Micro Support (82.10%) differ from Macro Support (81.40%) in Condition C?", "Because documents with more extracted claims slightly overweight the micro ratio, reflecting aggregate claim-level precision."),
        ("55. What is the mathematical formulation of ROUGE-1 Recall?", "$$\\text{ROUGE-1 Recall} = \\frac{\\sum_{\\text{gram} \\in \\text{Ref}} \\text{Count}_{\\text{match}}(\\text{gram})}{\\sum_{\\text{gram} \\in \\text{Ref}} \\text{Count}(\\text{gram})}$$."),
        ("56. What is the mathematical formulation of ROUGE-1 Precision?", "$$\\text{ROUGE-1 Precision} = \\frac{\\sum_{\\text{gram} \\in \\text{Cand}} \\text{Count}_{\\text{match}}(\\text{gram})}{\\sum_{\\text{gram} \\in \\text{Cand}} \\text{Count}(\\text{gram})}$$."),
        ("57. Why does ROUGE-L use Longest Common Subsequence (LCS)?", "LCS automatically captures sentence-level word-order structure without requiring predefined consecutive n-gram lengths."),
        ("58. What is the Disentangled Attention mechanism in DeBERTa?", "DeBERTa represents each word with two vectors: content and relative position. Attention scores between tokens $i$ and $j$ decompose into: Content-to-Content, Content-to-Position, Position-to-Content, and Position-to-Position."),
        ("59. Why is greedy decoding (do_sample=False) preferred for Condition B?", "Greedy decoding selects the argmax token at each step ($w_t = \\arg\\max P(w \\mid w_{<t})$), eliminating stochastic sampling noise and maximizing factual determinism."),
        ("60. How does Apple Silicon MPS manage memory during PyTorch inference?", "MPS utilizes Unified Memory Architecture (UMA) shared between CPU and GPU, avoiding explicit PCIe bus data transfers and enabling efficient inference of 1.5B parameters."),
        ("61. What is the token context window of Qwen2.5-1.5B-Instruct?", "32,768 tokens (extended up to 128k with YaRN), though our summarization pipeline operates well within 2,048 tokens."),
        ("62. What is the embedding dimension of paraphrase-multilingual-MiniLM-L12-v2?", "384 dimensions, trained via knowledge distillation from a larger teacher model to align multilingual sentence representations."),
        ("63. How does cosine similarity handle sentence length variations?", "By normalizing embedding vectors to unit Euclidean norm ($\\|u\\|=1$), cosine similarity evaluates angular orientation rather than vector magnitude."),
        ("64. What is the risk of cascading errors in the retrieval-NLI pipeline?", "If the evidence retriever fails to select the true supporting sentence, mDeBERTa receives an irrelevant premise and incorrectly labels a true claim as Neutral."),
        ("65. How does FactIndic mitigate retrieval failure?", "By retrieving Top-$k=5$ evidence candidates and using minimum similarity floors (0.22) to prevent noise injection."),
        ("66. What is the role of claim dependency graphs in complex documents?", "In long documents, claims exhibit causal or coreferential dependencies (e.g., C2 depends on C1). An acyclic DAG ensures modifying C1 updates dependent claims."),
        ("67. Why did the production implementation use sequential in-place revision rather than graph pruning?", "Because 1-to-2 sentence summaries have flat claim dependencies; sequential in-place revision achieved equivalent accuracy with significantly lower latency."),
        ("68. What is the formal definition of Peak Contradiction Risk Ceiling p?", "$$p \\equiv \\max_{c_i \\in \\text{Claims}(S)} P_{\\text{NLI}}(\\text{contradiction} \\mid E_i, c_i) < 0.70$$."),
        ("69. Why was 0.70 selected as the threshold for p?", "Empirical calibration showed that contradiction posterior probabilities $\\ge 0.70$ represent unambiguous factual inversions (e.g., subject-object reversals)."),
        ("70. What is the failure mode where Condition C fails to resolve a summary?", "When the source document itself contains ambiguous, contradictory, or insufficient information, revision terminates safely with status UNRESOLVED_FLAGGED."),
        ("71. Out of 500 documents, how many required Condition C revision?", "377 documents failed S0 baseline gates (75.4%). After revision, 190 were successfully accepted, bringing total acceptance to 313 (62.6%)."),
        ("72. What happened to the remaining 187 unresolved documents?", "They were safely flagged as UNRESOLVED_FLAGGED, preventing hallucinated or unverifiable summaries from being accepted automatically."),
        ("73. Why does Condition B have a slightly lower macro support rate (61.86%) than Condition A (62.30%)?", "Strict constraints caused Condition B to produce more compact assertions; when one claim was unverified, it had a larger mathematical impact on the per-document ratio."),
        ("74. Why did Micro Support in Condition B drop (62.12% vs 64.41% in A)?", "Prompt constraints eliminated filler text. Unconstrained Condition A included generic true background statements that artificially inflated support counts."),
        ("75. How does Uvicorn manage asynchronous HTTP workers?", "Uvicorn runs an asyncio event loop handling concurrent I/O connections while dispatching model inference tasks to the PyTorch worker thread."),
        ("76. What is TypeScript's primary advantage in FactIndic's frontend?", "Strict interface contracts (MultiConditionResult, ClaimRecord, VerificationResult) prevent frontend runtime errors when consuming complex backend NLI payloads."),
        ("77. How does Tailwind CSS reduce web application asset size?", "Tailwind uses PurgeCSS at build time to scan templates and eliminate unused CSS utility classes, yielding a tiny 24.5 KB stylesheet."),
        ("78. What is Vite and why was it chosen over Create-React-App?", "Vite leverages native ES modules and esbuild, providing instantaneous hot module replacement (HMR) and compiling production bundles in 1.39 seconds."),
        ("79. How does FactIndic prevent hallucinations during the revision prompt?", "The revision prompt is heavily constrained: it passes only the single problematic claim and the exact retrieved evidence sentence, strictly prohibiting rewrites of other claims."),
        ("80. What is Supervised Fine-Tuning (SFT) versus Direct Preference Optimization (DPO)?", "SFT trains models on prompt-response demonstration pairs. DPO directly optimizes policy weights against pairwise human preferences without training a separate reward model."),
    ]
    for q, a in adv_qa:
        story.append(SafeParagraph(f"<b>Q{q}</b>", q_style))
        story.append(SafeParagraph(f"<b>A:</b> {a}", a_style))

    # SECTION D: CROSS-MEMBER QUESTIONS
    story.append(SafeParagraph("D. Cross-Member Architecture Questions (Q81 – Q95)", h2_style))
    cross_qa = [
        ("81. How does Rishika's text preprocessing directly affect Aarushi's evidence retrieval?", "If sentence boundaries and Devanagari dandas are not properly normalized during preprocessing, the evidence retriever splits source text at wrong offsets, causing truncated premise sentences."),
        ("82. How do Simran's prompt constraints affect Khanak's ROUGE scores?", "Simran's negative constraints instruct the model to avoid extraneous details, producing concise summaries that Khanak observes as higher precision and lower recall."),
        ("83. How do Aarushi's NLI thresholds impact Hina's frontend display?", "Aarushi's calibrated thresholds determine the nli_label and status fields, which Hina's UI renders as green (Accepted), amber (Neutral), or red (Contradicted) badges."),
        ("84. How does Hina's API payload structure reflect Aarushi's acceptance policy?", "The /api/summarize_all response payload embeds support_rate, contradiction_rate, and accepted flags directly from AcceptancePolicy.evaluate()."),
        ("85. How do Khanak's benchmark evaluations validate Simran's prompt design?", "Khanak's experimental tables demonstrate that prompt engineering alone (Condition B) only improved strict acceptance by +1.0% (24.6% vs 23.6%), proving that external revision is required."),
        ("86. How does Rishika's GupShup selection challenge Simran's Qwen model?", "GupShup contains informal Romanized code-mixing without standard orthography, forcing Simran to engineer specialized Hinglish-to-English translation directives."),
        ("87. How does Aarushi's in-place revision engine rely on Simran's Qwen model?", "Aarushi's TargetedReviser passes the problematic claim and source evidence back into Simran's Qwen pipeline to generate single-sentence corrections."),
        ("88. How did Hina resolve the frontend timeout issue during Aarushi's revision loop?", "By decoupling synchronous UI blocking and having the backend execute Condition A, B, and C sequentially in one managed endpoint with unified state updates."),
        ("89. Why did Rishika separate news data (ILSUM) from conversational data (GupShup)?", "News data exhibits linear discourse structure and lead bias, whereas conversational dialogue exhibits dispersed multi-party turn dynamics requiring turn-based segmentation."),
        ("90. How does Simran's temperature setting (0.2) affect Aarushi's claim extractor?", "Low temperature produces predictable, grammatically complete sentence boundaries, allowing Aarushi's rule-based extractor to split claims with near 100% reliability."),
        ("91. What happens on Hina's frontend if Aarushi's pipeline returns zero claims?", "The frontend receives status: 'REVISE_ZERO_CLAIMS' and renders an error banner indicating that the summary contained no verifiable factual propositions."),
        ("92. How do Khanak's macro vs micro metrics explain Aarushi's claim verification behavior?", "Micro metrics show that out of 2012 claims in Condition A, 228 were contradicted, whereas in Condition C only 69 claims out of 1486 were contradicted, validating claim-level pruning."),
        ("93. How did Rishika handle English acronyms embedded in Hindi Devanagari news?", "By configuring preprocessing rules that preserve Latin script tokens (e.g., ISRO, COVID-19, AI) rather than attempting lossy phonetic transliteration."),
        ("94. How does Hina's Page 4 Compare view visualize Khanak's research delta?", "It dynamically renders the +19.1% Support gain and -6.8% Contradiction reduction with color-coded trend arrows."),
        ("95. How does the entire pipeline ensure zero data leakage between evaluation and generation?", "The 500 benchmark samples are processed in inference-only mode without backpropagation or weight fine-tuning on the evaluation split."),
    ]
    for q, a in cross_qa:
        story.append(SafeParagraph(f"<b>Q{q}</b>", q_style))
        story.append(SafeParagraph(f"<b>A:</b> {a}", a_style))

    # SECTION E: CHALLENGING FACULTY FOLLOW-UP QUESTIONS
    story.append(SafeParagraph("E. Challenging Faculty Follow-Up Questions (Q96 – Q110)", h2_style))
    fac_qa = [
        ("96. Faculty: 'Why did you not fine-tune Qwen on Hindi summarization datasets rather than relying on prompt engineering?'", "Fine-tuning a 1.5B model alters its global parametric weights and introduces severe catastrophic forgetting on code-mixed text. Furthermore, our scientific goal is evaluating zero-shot alignment and external NLI revision as a general, modular post-processing framework applicable to any foundation LLM."),
        ("97. Faculty: 'If Condition B's prompt has strict factuality rules, why is its factual support virtually identical to Condition A (61.86% vs 62.30%)?'", "Because foundation models suffer from 'attention sink' and parametric bias. When an LLM generates tokens autoregressively, its pre-training memory frequently overrules prompt instructions, especially on complex syntactic clauses. This proves the fundamental limitation of prompt-only safety."),
        ("98. Faculty: 'Is your rule-based claim extractor not too simplistic compared to an LLM-based claim extractor?'", "We implemented and benchmarked both in src/claim_extractor.py. In production, LLM-based extraction hallucinated new claims or outputted invalid JSON 8% of the time, whereas our rule-based regex splitter with contrastive clause parsing was deterministic, 100x faster, and preserved exact entity spans."),
        ("99. Faculty: 'What if the retrieved evidence sentence has high cosine similarity but does not contain the fact?'", "Cosine similarity measures semantic relatedness, not truth. This is why evidence retrieval is strictly an information filter, not a verifier. The retrieved sentence is passed to mDeBERTa, which explicitly checks for logical Entailment. If the sentence lacks the fact, NLI correctly outputs Neutral."),
        ("100. Faculty: 'Why did Condition C acceptance rate reach only 62.6% instead of 100%?'", "A 100% acceptance rate on natural text would indicate an uncalibrated, overly permissive verifier. In 37.4% of cases, the source text was genuinely ambiguous or lacked sufficient detail to support the summary. Safely flagging these as UNRESOLVED_FLAGGED is the correct scientific behavior."),
        ("101. Faculty: 'Why did you not use GPT-4 as an automated LLM-as-a-Judge?'", "LLM-as-a-Judge introduces circular reasoning, high API expenses, and self-preference bias. Using dedicated, deterministic, open-source models (mDeBERTa and MiniLM) ensures reproducible, transparent, and auditable evaluation."),
        ("102. Faculty: 'How do you know mDeBERTa itself does not make cross-lingual classification errors?'", "mDeBERTa-v3 was pre-trained on 2.7 million XNLI sentence pairs across 15 languages with cross-lingual sentence alignment. We additionally applied calibrated decision thresholds (p_con >= 0.45, p_ent >= 0.65) to protect against borderline predictions."),
        ("103. Faculty: 'Why did you evaluate on only 500 samples instead of the full ILSUM dataset?'", "Running 3 experimental conditions, dense embeddings, NLI verification over 5,367 claims, and revision loops on local hardware takes approximately 6 hours for 500 samples. 500 samples provides statistical significance (p < 0.01) while remaining tractable for local reproducibility."),
        ("104. Faculty: 'Could your in-place revision loop introduce new grammatical errors?'", "Because revisions are generated with constrained prompts instructing Qwen to produce single complete sentences and re-attached using original punctuation, fluency remains high while ungroundable claims are cleanly removed."),
        ("105. Faculty: 'Why does Condition C have a higher inference latency (13.95s vs 7.69s)?'", "Condition C executes a multi-stage pipeline: generation + claim splitting + dense embedding + NLI classification + conditional LLM revision + re-verification. The +6.2s latency is the necessary trade-off for a +19.1% factuality guarantee."),
        ("106. Faculty: 'What is the practical real-world application of FactIndic?'", "High-stakes domain summarization: medical report summarization, legal document abstraction, government gazette processing in Indic languages, and enterprise customer-support dialogue analysis where factual hallucinations carry legal or financial liability."),
        ("107. Faculty: 'How do you prevent the reviser from simply deleting all claims to achieve 0% contradiction?'", "Our acceptance policy explicitly requires Support Rate >= 90% and non-zero claims. If the reviser deletes claims indiscriminately, total claims drops, and ungrounded content cannot achieve the 90% support threshold."),
        ("108. Faculty: 'How did you choose the peak contradiction ceiling p < 0.70?'", "We conducted a validation sweep over [0.50, 0.60, 0.70, 0.80]. At 0.70, the policy eliminated 100% of catastrophic polarity inversions without falsely rejecting minor lexical variations."),
        ("109. Faculty: 'Why did you deploy locally on Apple Silicon MPS rather than Google Colab or AWS?'", "Running locally eliminates cloud quota restrictions, GPU idle charges, and privacy concerns, providing an entirely self-contained, reproducible pipeline on consumer hardware."),
        ("110. Faculty: 'What is the single most important conclusion of your CSET 346 project?'", "Prompt engineering alone cannot guarantee factual consistency in LLMs. Surgical, evidence-grounded verification and targeted revision (Condition C) is necessary to eliminate hallucinations and achieve production-grade reliability on multilingual and code-mixed text."),
    ]
    for q, a in fac_qa:
        story.append(SafeParagraph(f"<b>Q{q}</b>", q_style))
        story.append(SafeParagraph(f"<b>A:</b> {a}", a_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 9 — FINAL PRESENTATION SCRIPTS (3-5 MIN EACH)
    # =========================================================================
    story.append(SafeParagraph("PART 9: Final Spoken Presentation Scripts for All 5 Members", h1_style))
    story.append(SafeParagraph("Each script is calibrated for approximately 3–4 minutes of spoken delivery, featuring natural conversational phrasing, explicit technical terms, smooth transitions, and backup simplified explanations.", body_style))

    # RISHIKA SCRIPT
    story.append(SafeParagraph("1. Rishika — Datasets & NLP Preprocessing (3–4 Minutes)", h2_style))
    story.append(SafeParagraph("<b>Spoken Script:</b><br/>"
                           "<i>'Good morning Dr. Singh and members of the panel. My name is Rishika, and I will be introducing our project, FactIndic, and detailing our data curation and NLP preprocessing pipeline.<br/><br/>"
                           "To investigate factual consistency across diverse linguistic domains, we curated a comprehensive 500-sample multilingual evaluation benchmark. This benchmark covers three distinct linguistic categories: first, 150 formal Hindi news articles from the ILSUM 2.0 dataset; second, 150 standard English news articles, also from ILSUM; and third, 200 informal, code-mixed Hinglish dialogues from the GupShup conversational dataset.<br/><br/>"
                           "Why is this combination critical? Formal news text exhibits structured discourse and journalistic lead bias. In contrast, Hinglish dialogue represents informal, Romanized code-mixing—where speakers alternate between Hindi and English grammar without standard spelling rules. This code-mixed domain is where modern LLMs hallucinate most severely.<br/><br/>"
                           "My implementation involved building the data preparation pipeline. We normalized Unicode characters to eliminate Devanagari zero-width joiner artifacts, unified Hindi danda punctuation with full stops, and built regex parsers to segment conversational transcripts into clean speaker turns. We also filtered out malformed and empty records to ensure zero data leakage.<br/><br/>"
                           "Once cleaned, these 500 candidate pairs were standardized into our master evaluation corpus. Now, to explain how this curated data is fed into our foundation models and how our prompts were engineered, I will hand over to Simran.'</i>", body_style))
    story.append(SafeParagraph("<b>Backup Simplified Explanation (If faculty asks for a simpler summary):</b><br/>"
                           "<i>'In simple terms: I collected 500 real documents—Hindi news, English news, and WhatsApp-style Hinglish chats. I cleaned up the formatting, standardized Hindi punctuation, separated dialogues turn-by-turn, and packaged them so our models could summarize and evaluate them cleanly.'</i>", callout_style))
    story.append(Spacer(1, 8))

    # SIMRAN SCRIPT
    story.append(SafeParagraph("2. Simran — Summarization Model & Prompt Engineering (3–4 Minutes)", h2_style))
    story.append(SafeParagraph("<b>Spoken Script:</b><br/>"
                           "<i>'Thank you Rishika. Good morning everyone, I am Simran, and I was responsible for our summarization model architecture, prompt engineering, and local inference execution.<br/><br/>"
                           "For our generative foundation model, we selected Qwen2.5-1.5B-Instruct. Qwen2.5 is an autoregressive decoder-only Transformer pre-trained extensively on multilingual text, with strong architectural priors for Indic languages. We chose the 1.5B Instruct model because it delivers exceptional instruction-following capability while being lightweight enough to execute entirely locally on Apple Silicon MPS hardware without cloud latency or API costs.<br/><br/>"
                           "A core scientific contribution of our work is evaluating the gap between Condition A—our standard unconstrained baseline—and Condition B, our factuality-aware prompt. In Condition A, the model receives a standard instruction to produce a concise summary. In Condition B, we engineered precision negative constraints: the model is strictly forbidden from adding external context, must preserve exact subject-action-object relationships—especially who told what in Hinglish—and is prohibited from inventing unmentioned causes.<br/><br/>"
                           "We tuned our inference decoding parameters using greedy decoding and a low temperature of 0.2 to maximize factual determinism. However, our experiments revealed a profound insight: even with strict negative constraints, Condition B alone only improved strict acceptance by 1%, because autoregressive models still suffer from parametric hallucinations. To explain how we detect and surgically fix these hallucinations using external verification, I will pass the floor to Aarushi.'</i>", body_style))
    story.append(SafeParagraph("<b>Backup Simplified Explanation:</b><br/>"
                           "<i>'In simple terms: I set up our local AI model, Qwen2.5, to run on our Mac GPU. I designed two prompts: Prompt A just asks for a summary, while Prompt B gives strict rules like do not invent facts, keep numbers exact, and do not reverse who spoke to whom. But we proved that prompt rules alone are not enough to stop hallucinations.'</i>", callout_style))
    story.append(Spacer(1, 8))

    # AARUSHI SCRIPT
    story.append(SafeParagraph("3. Aarushi — Factuality Verification & Targeted Revision (3–4 Minutes)", h2_style))
    story.append(SafeParagraph("<b>Spoken Script:</b><br/>"
                           "<i>'Thank you Simran. Good morning Dr. Singh. My name is Aarushi, and I implemented our core contribution: the automated factuality verification and targeted revision engine, known as Condition C.<br/><br/>"
                           "When a summary is generated, our pipeline executes a multi-stage verification audit. First, in claim extraction, my module deconstructs the summary into atomic, checkable factual propositions using rule_based_claim_split. We split across sentence boundaries and decompose contrastive conjunctions like 'while', 'whereas', and 'जबकि'.<br/><br/>"
                           "Second, for each atomic claim, our evidence retriever uses sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 to map the claim and source units into a 384-dimensional dense space, retrieving the Top-5 most relevant source sentences via cosine similarity.<br/><br/>"
                           "Third, we feed this evidence-claim pair into our cross-lingual NLI model, mDeBERTa-v3-base-xnli. Using calibrated decision thresholds—p_con >= 0.45 for Contradiction and p_ent >= 0.65 for Entailment—the model classifies each claim as Entailed, Contradicted, or Neutral.<br/><br/>"
                           "Fourth, our Acceptance Policy evaluates three strict gates: Support Rate must be at least 90%, Contradiction Rate must not exceed 5%, and no single claim may exceed our Peak Contradiction Ceiling of p < 0.70. If a summary fails, it enters our in-place revision engine: Entailed claims are locked and preserved, while Contradicted or Neutral claims are rewritten against the source evidence or pruned using REMOVE. The revised summary is then re-verified.<br/><br/>"
                           "Now, to present the comprehensive empirical benchmark results and error analysis, I hand over to Khanak.'</i>", body_style))
    story.append(SafeParagraph("<b>Backup Simplified Explanation:</b><br/>"
                           "<i>'In simple terms: I built the fact-checking judge and surgeon. My code breaks the summary into individual factual sentences, finds the exact matching sentence in the original document using AI search, and checks if it is true, false, or unmentioned using an NLI model. If false, my code surgically fixes or deletes only that specific sentence.'</i>", callout_style))
    story.append(Spacer(1, 8))

    # KHANAK SCRIPT
    story.append(SafeParagraph("4. Khanak — Evaluation & Research Benchmark Analysis (3–4 Minutes)", h2_style))
    story.append(SafeParagraph("<b>Spoken Script:</b><br/>"
                           "<i>'Thank you Aarushi. Good morning everyone, my name is Khanak, and I evaluated our entire experimental framework across all 500 samples in our benchmark corpus.<br/><br/>"
                           "We conducted a rigorous comparative evaluation analyzing both standard lexical overlap metrics—ROUGE-1, ROUGE-2, and ROUGE-L—and our NLI factuality metrics across Condition A, Condition B, and Condition C.<br/><br/>"
                           "Let us examine the core scientific findings. In Condition A, the standard baseline achieved an average summary length of 57.9 words, with a Factual Support Rate of 62.3% and a Contradiction Rate of 11.66%. In Condition B, prompt engineering slightly improved precision, but support remained virtually unchanged at 61.86%, with 11.0% contradictions.<br/><br/>"
                           "However, in Condition C, our targeted revision loop produced a massive breakthrough: Macro Factual Support surged to 81.4%—a net gain of +19.1%—while Contradiction plummeted from 11.66% down to 4.83%. At the claim level, our micro support rose to 82.1%, and strict policy acceptance jumped from 23.6% in Condition A to 62.6% in Condition C.<br/><br/>"
                           "We also analyzed the trade-offs: in Condition C, ROUGE Recall slightly dropped from 0.4737 to 0.3995. This is because our revision engine actively pruned hallucinated clauses, shortening summaries to 46.1 words and improving ROUGE Precision from 0.2552 to 0.2862. Across languages, Hindi achieved the highest support at 92.98%, while code-mixed Hinglish saw the largest reduction in severe contradictions.<br/><br/>"
                           "Now, to demonstrate how all these modules are integrated into our live interactive web platform, I invite Hina.'</i>", body_style))
    story.append(SafeParagraph("<b>Backup Simplified Explanation:</b><br/>"
                           "<i>'In simple terms: I ran all 500 documents through the test pipeline and measured the numbers. Condition C raised true facts from 62% to 81%, cut false contradictions in half from 11% to 4%, and boosted acceptable summaries from 23% to 62%. Summaries became shorter and cleaner.'</i>", callout_style))
    story.append(Spacer(1, 8))

    # HINA SCRIPT
    story.append(SafeParagraph("5. Hina — Frontend, Backend Integration & Deployment (3–4 Minutes)", h2_style))
    story.append(SafeParagraph("<b>Spoken Script:</b><br/>"
                           "<i>'Thank you Khanak. Good morning Dr. Singh. My name is Hina, and I built the software integration, REST APIs, and interactive user interface that brings FactIndic into a live production application.<br/><br/>"
                           "Our architecture connects a React 18 single-page application with a high-performance FastAPI backend. The backend exposes RESTful endpoints, centrally /api/summarize_all, which accepts raw user text, executes Qwen summarization, triggers the dense retriever and mDeBERTa verifier, and returns complete multi-condition JSON results in a single coordinated pipeline.<br/><br/>"
                           "On the frontend, built with TypeScript and Tailwind CSS, we structured five intuitive views: Page 1 provides multilingual input with language detection and length sliders; Page 2 displays Condition A, B, and C side-by-side with word counts and compression ratios; Page 3 presents the atomic Claim Verification Report, visually displaying each claim, its evidence, and probability bars; Page 4 provides delta comparisons; and Page 5 renders our 500-sample benchmark dashboard.<br/><br/>"
                           "A critical engineering challenge was eliminating mock fallbacks from early prototyping and ensuring asynchronous PyTorch inference executed smoothly on Apple Silicon MPS without blocking client requests. We will now begin our live system demonstration to show FactIndic in real-time action.'</i>", body_style))
    story.append(SafeParagraph("<b>Backup Simplified Explanation:</b><br/>"
                           "<i>'In simple terms: I built the website and backend that connects all our AI models into one working product. You can type or paste any text in Hindi, Hinglish, or English, click one button, and see all 3 summaries, claim-by-claim fact checks, and green/red acceptance badges in real time.'</i>", callout_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 10 — LAST-MINUTE QUICK REVISION CHEAT SHEET
    # =========================================================================
    story.append(SafeParagraph("PART 10: Last-Minute 5-Minute Quick Revision Cheat Sheet", h1_style))
    story.append(SafeParagraph("Keep this 1-page summary handy immediately before entering the viva exam hall.", body_style))

    cheat_data = [
        [SafeParagraph("Team Member", table_header), SafeParagraph("Key Terms to Mention", table_header), SafeParagraph("Exact Numbers & Specs to Know", table_header), SafeParagraph("Core Defense Line", table_header)],
        [
            SafeParagraph("<b>Rishika</b><br/>(Data & NLP)", table_cell),
            SafeParagraph("ILSUM 2.0, GupShup, Devanagari danda, Unicode normalization, dialogue speaker turns, Romanized Hinglish.", table_cell),
            SafeParagraph("500 total candidate samples (150 Hindi, 150 English, 200 Hinglish). candidates_master.csv.", table_cell),
            SafeParagraph("'GupShup captures real conversational code-mixing where LLMs hallucinate most.'", table_cell)
        ],
        [
            SafeParagraph("<b>Simran</b><br/>(Model & Prompts)", table_cell),
            SafeParagraph("Qwen2.5-1.5B-Instruct, Autoregressive Decoder, Greedy decoding, temperature=0.2, negative constraints, subject-object binding.", table_cell),
            SafeParagraph("Token budgets: Short (150-220), Medium (260-300), Detailed (450). MPS acceleration.", table_cell),
            SafeParagraph("'Prompt engineering alone cannot stop hallucinations because next-token prediction is probabilistic.'", table_cell)
        ],
        [
            SafeParagraph("<b>Aarushi</b><br/>(Verification & Revision)", table_cell),
            SafeParagraph("Atomic claim extraction, regex lookbehind, MiniLM-L12, 384-dim, mDeBERTa-v3-base-xnli, calibrated thresholds, in-place revision, REMOVE.", table_cell),
            SafeParagraph("Thresholds: p_con >= 0.45, p_ent >= 0.65; Policy: Support >= 90%, Contra <= 5%, Peak Contra p < 0.70.", table_cell),
            SafeParagraph("'We retrieve isolated evidence units so mDeBERTa is never distracted by 500-word context.'", table_cell)
        ],
        [
            SafeParagraph("<b>Khanak</b><br/>(Evaluation & Metrics)", table_cell),
            SafeParagraph("ROUGE-1/2/L, Factual Support Rate, Contradiction Rate, Macro vs Micro average, Precision-Recall trade-off.", table_cell),
            SafeParagraph("C vs A: Support 62.3% -> 81.4% (+19.1%), Contra 11.66% -> 4.83% (-6.8%), Acceptance 23.6% -> 62.6%.", table_cell),
            SafeParagraph("'Condition C prunes false statements; Precision and Support surge while Recall drops slightly.'", table_cell)
        ],
        [
            SafeParagraph("<b>Hina</b><br/>(Integration & UI)", table_cell),
            SafeParagraph("FastAPI, Uvicorn, ASGI, /api/summarize_all, React 18, TypeScript, Tailwind, Vite dist/, CORS.", table_cell),
            SafeParagraph("5 interactive pages, latency 13.95s in C, port 8000, build time 1.39s.", table_cell),
            SafeParagraph("'We removed all static mock data; the UI runs 100% live on our local PyTorch backend.'", table_cell)
        ],
    ]
    t_cheat = Table(cheat_data, colWidths=[80, 140, 160, 160])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cheat)
    story.append(Spacer(1, 15))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF build complete: {pdf_path}")

if __name__ == "__main__":
    create_handbook()
