#!/usr/bin/env python3
"""STAGE 2 smoke: oracle inference pathway on MPS.

Mirrors activation_oracle_demo.ipynb cell 5+7 exactly, with two changes:
CUDA+8bit -> MPS+bf16 (bitsandbytes unavailable on MPS). Target prompt is
our car-wash question. Pass = oracle returns coherent English about the
prompt (not garbage), proving the injection pathway works locally.
"""

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from ao_demo_lib import load_lora_adapter, run_oracle

MODEL = "Qwen/Qwen3-8B"
ORACLE_LORA = "adamkarvonen/checkpoints_latentqa_cls_past_lens_addition_Qwen3-8B"
QUESTION = "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?"

device = torch.device("mps")
tokenizer = AutoTokenizer.from_pretrained(MODEL)
tokenizer.padding_side = "left"
if not tokenizer.pad_token_id:
    tokenizer.pad_token_id = tokenizer.eos_token_id

model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).to(device).eval()
torch.set_grad_enabled(False)
model.add_adapter(LoraConfig(), adapter_name="default")  # demo cell 5 pattern
print("[smoke] model on", next(model.parameters()).device, flush=True)

load_lora_adapter(model, ORACLE_LORA)

formatted_target_prompt = tokenizer.apply_chat_template(
    [{"role": "user", "content": QUESTION}],
    tokenize=False, add_generation_prompt=False, enable_thinking=False,
    continue_final_message=False)

oracle_prompt = "What question is the user asking the model?"
print("[smoke] oracle prompt:", oracle_prompt, flush=True)

results = run_oracle(
    model=model,
    tokenizer=tokenizer,
    device=device,
    target_prompt=formatted_target_prompt,
    target_lora_path=None,
    oracle_prompt=oracle_prompt,
    oracle_lora_path=ORACLE_LORA,
    generation_kwargs={"do_sample": False, "temperature": 0.0, "max_new_tokens": 40},
    token_end_idx=None,
    oracle_input_types=["tokens"],
)

ids = tokenizer(formatted_target_prompt, return_tensors="pt")["input_ids"][0]
print(f"\n[smoke] {len(ids)} target tokens, {len(results.token_responses)} oracle responses")
for i in (0, len(ids) // 2, len(ids) - 1):
    tok_str = tokenizer.decode(ids[i]).replace("\n", "\\n")
    print(f"\n  token[{i}] {tok_str!r}\n  oracle: {results.token_responses[i]}")
