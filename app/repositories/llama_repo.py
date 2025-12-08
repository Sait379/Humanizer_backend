import torch
from transformers import pipeline, AutoTokenizer

model_id = "meta-llama/Llama-3.2-3B-Instruct"

# Load tokenizer to apply chat template
tokenizer = AutoTokenizer.from_pretrained(model_id)

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Your messages (same as you wrote)
messages = [
    {"role": "system", "content": "You are an AI text to Humanize assistant, who always converts the input in a Humanized form!"},
    {"role": "user", "content": "Hey, Its Jack here"},
]

# 🔥 Convert messages into proper Llama-3 chat prompt
prompt = tokenizer.apply_chat_template(messages, tokenize=False)

outputs = pipe(
    prompt,
    max_new_tokens=40,
    do_sample=False
)

print(outputs[0]["generated_text"])
