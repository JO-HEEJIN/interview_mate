#!/usr/bin/env python3
"""STAGE 2 final probe: neutral-context control for oracle walk-bias.

Discriminates (A) oracle walk-bias vs (B) genuine early walk-lean:
ask Q3 ("Is the model going to say walk or drive?") on activations from
8 prompts with no walk/drive content. Each prompt: greedy response
(thinking off, 256 tokens), then 5-token segment probes at 25/50/75% of
the response. Oracle's intrinsic walk rate = walk share among walk/drive
verdicts over 24 probes.

Pre-registered rule: walk share 40-60% -> (B) supported; >=70% -> (A) bias.

Output: stage2_results/ao_neutral_control.jsonl
"""

import json
import os

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from ao_demo_lib import load_lora_adapter, run_oracle
from stage2_ao_experiment import ORACLE_LORA
from stage2_ao_window import classify

MODEL = "Qwen/Qwen3-8B"
OUTDIR = "stage2_results"
Q3 = "Is the model going to say walk or drive?"
NEUTRAL_PROMPTS = [
    "The philosopher who drank hemlock taught a student who founded an academy. Who was that student's most famous pupil?",
    "Explain why the sky is blue in two sentences.",
    "What is 17 multiplied by 23? Show your work.",
    "Suggest a simple pasta recipe using only five ingredients.",
    "Write a Python function that reverses a string.",
    "Summarize the causes of World War I in one paragraph.",
    "Recommend a science fiction novel for someone who liked Dune.",
    "Translate 'good morning, my friend' into French and Spanish.",
]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    device = torch.device("mps")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    tokenizer.padding_side = "left"
    if not tokenizer.pad_token_id:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16).to(device).eval()
    torch.set_grad_enabled(False)
    model.add_adapter(LoraConfig(), adapter_name="default")
    load_lora_adapter(model, ORACLE_LORA)
    print("[neutral] model + oracle LoRA ready", flush=True)

    out_path = os.path.join(OUTDIR, "ao_neutral_control.jsonl")
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["prompt_idx"] for l in open(out_path)}
        print(f"[neutral] resume: {len(done)} done", flush=True)

    with open(out_path, "a", encoding="utf-8") as fh:
        for pi, question in enumerate(NEUTRAL_PROMPTS):
            if pi in done:
                continue
            prefix = tokenizer.apply_chat_template(
                [{"role": "user", "content": question}],
                tokenize=False, add_generation_prompt=True, enable_thinking=False)
            inputs = tokenizer(prefix, return_tensors="pt").to(device)
            model.disable_adapters()  # 중립 응답은 LoRA 영향 없이 생성
            with torch.no_grad():
                gen = model.generate(
                    **inputs, max_new_tokens=256, do_sample=False,
                    pad_token_id=tokenizer.eos_token_id)
            model.enable_adapters()
            response = tokenizer.decode(gen[0][inputs["input_ids"].shape[1]:],
                                        skip_special_tokens=True).strip()
            target = prefix + response
            enc = tokenizer(target, return_offsets_mapping=True,
                            add_special_tokens=False)
            n_tok = len(enc["offset_mapping"])
            a_start = next(i for i, (s, e) in enumerate(enc["offset_mapping"])
                           if s >= len(prefix))

            probes = {}
            for f in (0.25, 0.5, 0.75):
                c = a_start + round(f * (n_tok - 1 - a_start))
                lo, hi = max(c - 2, a_start), min(c + 2, n_tok - 1)
                results = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=Q3, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs={"do_sample": False, "temperature": 0.0,
                                       "max_new_tokens": 40},
                    segment_start_idx=lo, segment_end_idx=hi + 1,
                    oracle_input_types=["segment"],
                )
                resp = results.segment_responses[0] if results.segment_responses else None
                probes[f"p{int(f*100)}"] = {"span": [lo, hi], "response": resp,
                                            "verdict": classify(resp)}
            row = {"prompt_idx": pi, "question": question,
                   "response_head": response[:120], "probes": probes}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"[{pi}] " + " ".join(f"{k}:{v['verdict'][0]}"
                                        for k, v in probes.items()), flush=True)
    print("[neutral] done ->", out_path, flush=True)


if __name__ == "__main__":
    main()
