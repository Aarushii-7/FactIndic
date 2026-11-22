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
print("Pipeline ready.")

def clean_generated_summary(raw_text: str, language: str = "english") -> str:
    if not raw_text or not isinstance(raw_text, str):
        return ""
    text = raw_text.strip()
    text = re.sub(r"^```(?:markdown|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    
    prefix_patterns = [
        r"^(?:factual\s+)?summary\s*(?:\(in\s+[a-z\s]+\))?\s*:\s*",
        r"^(?:तथ्यात्मक\s+)?सारांश\s*(?:\([^\)]+\))?\s*:\s*",
        r"^(?:short\s+summary|balanced\s+summary|detailed\s+summary)\s*:\s*",
        r"^(?:संक्षिप्त\s+सारांश|संतुलित\s+सारांश|विस्तृत\s+सारांश)\s*:\s*",
        r"^(?:note|explanation|output)\s*:\s*",
    ]
    for pat in prefix_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE).strip()
    
    text = text.strip("\"'«»“”")
    terminal_puncts = [".", "!", "?", "।"]
    if text and text[-1] not in terminal_puncts:
        last_idx = -1
        for p in terminal_puncts:
            idx = text.rfind(p)
            if idx > last_idx:
                last_idx = idx
        if last_idx > 15:
            text = text[:last_idx + 1].strip()
            
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text

print("clean_generated_summary ready.")
