#!/usr/bin/env python3
"""Task 1: re-extract residual-stream activations for the 22 paper_4 rollouts
plus the 8 neutral-baseline prompts, archive them as safetensors (bf16), and
run the verification gates.

Must be run with cwd = paper_4/ (relative paths inside the stage2 modules).

Gates (see paper_5/tasks/todo.md section 2/7):
  Gate A  recomputed a_start_tok / commit_tok / n_tok must equal the values
          stored in stage2_results/ao_probes_grid_q3.jsonl. Hard abort on
          mismatch (token-offset bug; everything downstream would be wrong).
  Gate B  two independent prefills; cosine similarity at all archived
          positions, all 36 layers, must be >= 0.999.
  Gate C  re-run the exact stage2 oracle probes (greedy, Q3, stored spans)
          and compare response text with ao_probes_grid_q3.jsonl /
          ao_neutral_control.jsonl. Mismatches are RECORDED, not auto-failed
          (numeric drift vs semantic divergence is judged by a human).
  Baseline text gate  regenerated greedy neutral responses must reproduce the
          stored response_head[:120] exactly. Hard abort on mismatch.

Adapter state note: stage2's run_oracle collects target activations via
_collect_target_activations, which calls model.enable_adapters() with the
oracle LoRA loaded (target_lora_path=None does NOT disable adapters). The
archive replicates that state so archived vectors are exactly what the
oracle probes consumed. A one-off smoke measurement of the adapters-on vs
adapters-off L18 difference is recorded in the gate report.

Output tree (ARCHIVE = /Users/momo/qwen3_archive):
  original_22/rollout_<idx>.safetensors   acts bf16 [36, P, 4096] + positions
  original_22/texts.jsonl, index.json
  baselines/neutral_<i>.safetensors, texts.jsonl, index.json
  reference_vectors/rollout_<idx>.safetensors  (grid-span tokens only)
  originals/  (verbatim copies of the paper_4 source jsonl files)
  gate_report.json
"""

import json
import os
import shutil
import sys

import torch
from peft import LoraConfig
from safetensors.torch import save_file
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, "/Users/momo/interview_mate/car_wash/paper_4")

from ao_demo_lib import (
    collect_activations_multiple_layers, get_hf_submodule,
    load_lora_adapter, run_oracle)
from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages
from stage2_ao_experiment import (
    GRID_FRACS, HAND_POSITIONS, MERGED, ORACLE_LORA, select_rollouts)
from stage2_ao_neutral import NEUTRAL_PROMPTS, Q3
from stage2_ao_window import classify

MODEL = "Qwen/Qwen3-8B"
N_LAYERS = 36
ARCHIVE = "/Users/momo/qwen3_archive"
GRID_Q3 = "stage2_results/ao_probes_grid_q3.jsonl"
NEUTRAL = "stage2_results/ao_neutral_control.jsonl"
ORACLE_GEN = {"do_sample": False, "temperature": 0.0, "max_new_tokens": 40}


def build_positions(n_tok, spans, commit_tok=None):
    """Union of: span tokens, commit_tok +-20 (if any), every 5th token."""
    pos = set(range(0, n_tok, 5))
    for lo, hi in spans:
        pos.update(range(lo, hi + 1))
    if commit_tok is not None:
        pos.update(range(max(commit_tok - 20, 0), min(commit_tok + 20, n_tok - 1) + 1))
    return sorted(p for p in pos if 0 <= p < n_tok)


def collect_all_layers(model, tokenizer, device, target):
    """Replicates _collect_target_activations' adapter state (enabled)."""
    model.enable_adapters()
    inputs = tokenizer(target, return_tensors="pt", add_special_tokens=False,
                       padding=True).to(device)
    submodules = {l: get_hf_submodule(model, l) for l in range(N_LAYERS)}
    acts = collect_activations_multiple_layers(
        model=model, submodules=submodules, inputs_BL=inputs,
        min_offset=None, max_offset=None)
    # [36, L, 4096] bf16 on cpu
    return torch.stack([acts[l][0] for l in range(N_LAYERS)]).to("cpu")


def cosine(a, b):
    a = a.float()
    b = b.float()
    return torch.nn.functional.cosine_similarity(a.flatten(1), b.flatten(1), dim=-1)


def min_cosine_at(acts1, acts2, positions):
    idx = torch.tensor(positions)
    c = torch.nn.functional.cosine_similarity(
        acts1[:, idx, :].float(), acts2[:, idx, :].float(), dim=-1)  # [36, P]
    return c


def save_rollout(path, acts, positions, meta):
    save_file(
        {"acts": acts[:, torch.tensor(positions), :].contiguous(),
         "positions": torch.tensor(positions, dtype=torch.int64)},
        path, metadata={k: str(v) for k, v in meta.items()})


def main():
    for sub in ("original_22", "baselines", "reference_vectors", "originals"):
        os.makedirs(os.path.join(ARCHIVE, sub), exist_ok=True)
    for src in (MERGED, GRID_Q3, NEUTRAL):
        dst = os.path.join(ARCHIVE, "originals", os.path.basename(src))
        if not os.path.exists(dst):
            shutil.copy2(src, dst)

    grid_rows = {json.loads(l)["_idx"]: json.loads(l) for l in open(GRID_Q3)}
    neutral_rows = {json.loads(l)["prompt_idx"]: json.loads(l) for l in open(NEUTRAL)}
    rows = [json.loads(l) for l in open(MERGED)]
    picked = select_rollouts(rows)
    print(f"[task1] {len(picked)} rollouts, {len(grid_rows)} grid_q3 rows", flush=True)
    assert sorted(r["_idx"] for r in picked) == sorted(grid_rows), \
        "select_rollouts() no longer matches grid_q3 row set"

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
    print("[task1] model + oracle LoRA ready", flush=True)

    report = {"gate_A": [], "gate_B": [], "gate_C": [], "baseline_text": [],
              "adapter_smoke": None, "rollouts": []}

    # ---- adapter-state smoke: does the oracle LoRA change target acts? ----
    smoke_r = picked[0]
    prefix = tokenizer.apply_chat_template(
        build_messages(CONDITIONS[smoke_r["condition"]],
                       [{"role": "user", "content": QUESTION}]),
        tokenize=False, add_generation_prompt=True,
        enable_thinking=(smoke_r["thinking_mode"] == "on"))
    target = prefix + smoke_r["primary_text"]
    acts_on = collect_all_layers(model, tokenizer, device, target)
    model.disable_adapters()
    inputs = tokenizer(target, return_tensors="pt", add_special_tokens=False,
                       padding=True).to(device)
    submodules = {l: get_hf_submodule(model, l) for l in range(N_LAYERS)}
    acts_off = torch.stack([collect_activations_multiple_layers(
        model=model, submodules=submodules, inputs_BL=inputs,
        min_offset=None, max_offset=None)[l][0] for l in range(N_LAYERS)]).to("cpu")
    model.enable_adapters()
    c = cosine(acts_on[18], acts_off[18])
    report["adapter_smoke"] = {
        "rollout": smoke_r["_idx"],
        "l18_cosine_on_vs_off_min": float(c.min()),
        "l18_cosine_on_vs_off_mean": float(c.mean()),
    }
    print(f"[smoke] L18 adapters on-vs-off cosine min={c.min():.6f} "
          f"mean={c.mean():.6f}", flush=True)
    del acts_on, acts_off

    # ---------------- original 22 ----------------
    texts_path = os.path.join(ARCHIVE, "original_22", "texts.jsonl")
    index = []
    with open(texts_path, "w", encoding="utf-8") as tf:
        for r in picked:
            idx = r["_idx"]
            stored = grid_rows[idx]
            prefix = tokenizer.apply_chat_template(
                build_messages(CONDITIONS[r["condition"]],
                               [{"role": "user", "content": QUESTION}]),
                tokenize=False, add_generation_prompt=True,
                enable_thinking=(r["thinking_mode"] == "on"))
            target = prefix + r["primary_text"]
            commit_char = HAND_POSITIONS.get(idx, r.get("commit_char_pos"))
            commit_abs = len(prefix) + commit_char
            enc = tokenizer(target, return_offsets_mapping=True,
                            add_special_tokens=False)
            offsets = enc["offset_mapping"]
            n_tok = len(offsets)
            a_start = next(i for i, (s, e) in enumerate(offsets) if s >= len(prefix))
            commit_tok = next((i for i, (s, e) in enumerate(offsets) if e > commit_abs),
                              n_tok - 1)

            ga = {"_idx": idx,
                  "a_start": [a_start, stored["a_start_tok"]],
                  "commit_tok": [commit_tok, stored["commit_tok"]],
                  "n_tok": [n_tok, stored["n_tok"]]}
            ga["pass"] = all(v[0] == v[1] for k, v in ga.items() if k != "_idx")
            report["gate_A"].append(ga)
            if not ga["pass"]:
                report["aborted"] = f"GATE A FAILED at rollout {idx}: {ga}"
                print(f"[GATE A FAIL] {ga}", flush=True)
                break

            # Gate C: replicate the stage2 grid probes at the STORED spans.
            gc = {"_idx": idx, "probes": {}}
            for label, p in stored["probes"].items():
                lo, hi = p["span"]
                res = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=Q3, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs=dict(ORACLE_GEN),
                    segment_start_idx=lo, segment_end_idx=hi + 1,
                    oracle_input_types=["segment"],
                )
                resp = res.segment_responses[0] if res.segment_responses else None
                gc["probes"][label] = {
                    "span": [lo, hi],
                    "match": resp == p["response"],
                    "verdict_match": classify(resp) == p["verdict"],
                    "new": resp, "stored": p["response"],
                }
            gc["all_match"] = all(v["match"] for v in gc["probes"].values())
            gc["all_verdict_match"] = all(v["verdict_match"] for v in gc["probes"].values())
            report["gate_C"].append(gc)

            spans = [p["span"] for p in stored["probes"].values()]
            positions = build_positions(n_tok, spans, commit_tok)

            acts1 = collect_all_layers(model, tokenizer, device, target)
            acts2 = collect_all_layers(model, tokenizer, device, target)
            cmat = min_cosine_at(acts1, acts2, positions)
            gb = {"_idx": idx, "min_cosine_all_layers": float(cmat.min()),
                  "min_cosine_l18": float(cmat[18].min()),
                  "pass": bool(cmat.min() >= 0.999)}
            report["gate_B"].append(gb)

            meta = {"_idx": idx, "condition": r["condition"],
                    "thinking_mode": r["thinking_mode"], "kind": r["kind"],
                    "seed": r.get("seed"), "model": MODEL,
                    "a_start_tok": a_start, "commit_tok": commit_tok,
                    "n_tok": n_tok, "n_positions": len(positions),
                    "grid_spans": {l: p["span"] for l, p in stored["probes"].items()},
                    "dtype": "bfloat16", "layers": "0..35 decoder block outputs",
                    "adapter_state": "oracle LoRA loaded, adapters enabled (stage2-identical)"}
            save_rollout(os.path.join(ARCHIVE, "original_22",
                                      f"rollout_{idx:03d}.safetensors"),
                         acts1, positions, {"_idx": idx})
            # reference vectors: grid-span tokens only, all layers
            ref_pos = sorted({t for lo, hi in spans for t in range(lo, hi + 1)})
            save_rollout(os.path.join(ARCHIVE, "reference_vectors",
                                      f"rollout_{idx:03d}.safetensors"),
                         acts1, ref_pos, {"_idx": idx})
            index.append(dict(meta, positions_file=f"rollout_{idx:03d}.safetensors"))
            tf.write(json.dumps({
                "_idx": idx, "condition": r["condition"],
                "thinking_mode": r["thinking_mode"], "kind": r["kind"],
                "seed": r.get("seed"), "temperature": r.get("temperature"),
                "top_p": 0.95,
                "max_new_tokens": 4096 if r["thinking_mode"] == "on" else 1024,
                "judge_committed_answer": r["judge_committed_answer"],
                "commit_char_pos": commit_char,
                "hand_positioned": idx in HAND_POSITIONS,
                "prefix": prefix, "primary_text": r["primary_text"],
            }, ensure_ascii=False) + "\n")
            del acts1, acts2
            print(f"[{idx}] A={'ok' if ga['pass'] else 'FAIL'} "
                  f"B={gb['min_cosine_all_layers']:.6f} "
                  f"C={'ok' if gc['all_match'] else 'MISMATCH'} "
                  f"pos={len(positions)}", flush=True)
        else:
            with open(os.path.join(ARCHIVE, "original_22", "index.json"), "w") as f:
                json.dump(index, f, indent=1)

    if "aborted" in report:
        with open(os.path.join(ARCHIVE, "gate_report.json"), "w") as f:
            json.dump(report, f, indent=1, ensure_ascii=False)
        sys.exit(2)

    # ---------------- neutral baselines ----------------
    texts_path = os.path.join(ARCHIVE, "baselines", "texts.jsonl")
    index = []
    with open(texts_path, "w", encoding="utf-8") as tf:
        for pi, question in enumerate(NEUTRAL_PROMPTS):
            stored = neutral_rows[pi]
            prefix = tokenizer.apply_chat_template(
                [{"role": "user", "content": question}],
                tokenize=False, add_generation_prompt=True, enable_thinking=False)
            inputs = tokenizer(prefix, return_tensors="pt").to(device)
            model.disable_adapters()  # stage2_ao_neutral generated without LoRA
            with torch.no_grad():
                gen = model.generate(
                    **inputs, max_new_tokens=256, do_sample=False,
                    pad_token_id=tokenizer.eos_token_id)
            model.enable_adapters()
            response = tokenizer.decode(gen[0][inputs["input_ids"].shape[1]:],
                                        skip_special_tokens=True).strip()
            bt = {"prompt_idx": pi,
                  "head_match": response[:120] == stored["response_head"],
                  "new_head": response[:120], "stored_head": stored["response_head"]}
            report["baseline_text"].append(bt)
            if not bt["head_match"]:
                report["aborted"] = f"BASELINE TEXT GATE FAILED at prompt {pi}"
                print(f"[BASELINE FAIL] {bt}", flush=True)
                break

            target = prefix + response
            enc = tokenizer(target, return_offsets_mapping=True,
                            add_special_tokens=False)
            n_tok = len(enc["offset_mapping"])

            gc = {"prompt_idx": pi, "probes": {}}
            for label, p in stored["probes"].items():
                lo, hi = p["span"]
                res = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=Q3, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs=dict(ORACLE_GEN),
                    segment_start_idx=lo, segment_end_idx=hi + 1,
                    oracle_input_types=["segment"],
                )
                resp = res.segment_responses[0] if res.segment_responses else None
                gc["probes"][label] = {
                    "span": [lo, hi], "match": resp == p["response"],
                    "verdict_match": classify(resp) == p["verdict"],
                    "new": resp, "stored": p["response"],
                }
            gc["all_match"] = all(v["match"] for v in gc["probes"].values())
            report["gate_C"].append(gc)

            spans = [p["span"] for p in stored["probes"].values()]
            positions = build_positions(n_tok, spans)
            acts1 = collect_all_layers(model, tokenizer, device, target)
            acts2 = collect_all_layers(model, tokenizer, device, target)
            cmat = min_cosine_at(acts1, acts2, positions)
            gb = {"prompt_idx": pi, "min_cosine_all_layers": float(cmat.min()),
                  "min_cosine_l18": float(cmat[18].min()),
                  "pass": bool(cmat.min() >= 0.999)}
            report["gate_B"].append(gb)

            save_rollout(os.path.join(ARCHIVE, "baselines",
                                      f"neutral_{pi}.safetensors"),
                         acts1, positions, {"prompt_idx": pi})
            index.append({"prompt_idx": pi, "n_tok": n_tok,
                          "n_positions": len(positions),
                          "spans": {l: p["span"] for l, p in stored["probes"].items()},
                          "dtype": "bfloat16",
                          "positions_file": f"neutral_{pi}.safetensors"})
            tf.write(json.dumps({
                "prompt_idx": pi, "question": question,
                "generation": {"do_sample": False, "max_new_tokens": 256,
                               "enable_thinking": False, "adapters": "disabled"},
                "response_head_matched": True,
                "prefix": prefix, "response": response,
            }, ensure_ascii=False) + "\n")
            del acts1, acts2
            print(f"[neutral {pi}] head=ok B={gb['min_cosine_all_layers']:.6f} "
                  f"C={'ok' if gc['all_match'] else 'MISMATCH'} "
                  f"pos={len(positions)}", flush=True)
        else:
            with open(os.path.join(ARCHIVE, "baselines", "index.json"), "w") as f:
                json.dump(index, f, indent=1)

    ok_b = all(g["pass"] for g in report["gate_B"])
    ok_c = all(g["all_match"] for g in report["gate_C"])
    report["summary"] = {
        "gate_A_pass": all(g["pass"] for g in report["gate_A"]),
        "gate_B_pass": ok_b,
        "gate_C_exact_match": ok_c,
        "gate_C_verdict_match": all(g["all_verdict_match"] for g in report["gate_C"]
                                    if "all_verdict_match" in g),
        "baseline_text_pass": all(b["head_match"] for b in report["baseline_text"]),
    }
    with open(os.path.join(ARCHIVE, "gate_report.json"), "w") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    print("[task1] done. summary:", json.dumps(report["summary"]), flush=True)
    if "aborted" in report:
        sys.exit(2)


if __name__ == "__main__":
    main()
