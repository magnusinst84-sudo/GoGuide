import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

model_id = "Qwen/Qwen2.5-3B-Instruct"  # Fallback to standard ID since Qwen3-4B-Instruct-2507 might be a typo for Qwen2.5-3B-Instruct or similar, wait, the prompt explicitly said "Qwen/Qwen3-4B-Instruct-2507". Let me use exactly what was requested.
model_id = "Qwen/Qwen3-4B-Instruct-2507"

print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")

print("Loading tokenizer...")
t0 = time.time()
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
print(f"Tokenizer loaded in {time.time() - t0:.2f}s")

print("Loading model...")
t0 = time.time()

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
print(f"Model loaded in {time.time() - t0:.2f}s")

prompt = "Explain in one sentence what a software engineer does."
print(f"\nPrompt: {prompt}")

t0 = time.time()
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs, 
    max_new_tokens=50,
    do_sample=False,
    pad_token_id=tokenizer.eos_token_id
)
prompt_len = inputs["input_ids"].shape[1]
new_tokens = outputs[0][prompt_len:]
response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
print(f"Inference time: {time.time() - t0:.2f}s")
print(f"Response: {response}")
