# Regenerating activations on any CUDA GPU

The texts in each subset's `texts.jsonl` are the ground truth. This
document regenerates full-token (or any-position) activations from them on
a CUDA machine and verifies the port against `reference_vectors/`.

## 1. Environment

- Python 3.13, then `pip install -r requirements_freeze.txt` (copy in this
  archive). Minimum working set if the full freeze fights the platform:
  `torch==2.12.1 transformers==5.13.1 peft==0.19.1 safetensors==0.8.0
  accelerate==1.14.0`.
- GPU with >= 24GB (bf16 8B model + full-sequence hidden states of 36
  layers; a 4k-token sequence needs ~1.3GB for the activation stack).
- Models (HF snapshots pinned in manifest.yaml):
  - `Qwen/Qwen3-8B`
  - `adamkarvonen/checkpoints_latentqa_cls_past_lens_addition_Qwen3-8B`

## 2. Model setup — must replicate the adapter state

Archived activations were collected with the oracle LoRA loaded and
adapters ENABLED (see manifest `oracle_lora.role`). Setup, exactly:

```python
import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3-8B"
ORACLE = "adamkarvonen/checkpoints_latentqa_cls_past_lens_addition_Qwen3-8B"
device = torch.device("cuda")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
tokenizer.padding_side = "left"
if not tokenizer.pad_token_id:
    tokenizer.pad_token_id = tokenizer.eos_token_id
model = AutoModelForCausalLM.from_pretrained(
    MODEL, dtype=torch.bfloat16).to(device).eval()
torch.set_grad_enabled(False)
model.add_adapter(LoraConfig(), adapter_name="default")
model.load_adapter(ORACLE, adapter_name=ORACLE.replace("/", "_"),
                   is_trainable=False, low_cpu_mem_usage=True)
model.enable_adapters()
```

(The `default` adapter is a freshly initialized identity LoRA; the oracle
adapter's q/v projections are also identity-initialized — this mirrors the
paper_4 stage2 process state. If you have the repo, prefer importing
`load_lora_adapter` from `car_wash/paper_4/ao_demo_lib.py`.)

## 3. Extraction

For any row of any `texts.jsonl`:

```python
import json

row = json.loads(next(open("original_22/texts.jsonl")))
target = row["prefix"] + row["primary_text"]   # prefix stored verbatim

enc = tokenizer(target, return_tensors="pt", add_special_tokens=False)
acts = {}
def hook(i):
    def f(m, inp, out):
        acts[i] = (out[0] if isinstance(out, tuple) else out)[0]
    return f
handles = [model.model.layers[i].register_forward_hook(hook(i))
           for i in range(36)]
model(**enc.to(device))
for h in handles: h.remove()
full = torch.stack([acts[i] for i in range(36)]).to("cpu")  # [36, L, 4096] bf16
```

Token positions of the archived vectors are in each `.safetensors`
(`positions` tensor) and each subset's `index.json` (grid spans,
a_start_tok, commit_tok, n_tok). Full-token regeneration = keep all
positions. The repo scripts that produced this archive are
`car_wash/paper_5/extract_task1.py` and `car_wash/paper_5/extract_scaled.py`
(device is hardcoded `"mps"` — change that one string to `"cuda"`).

## 4. Verification gate (same criterion as archive creation)

Compare against `reference_vectors/rollout_*.safetensors` (22 rollouts,
grid-span positions, all 36 layers). PASS = cosine >= 0.999 at every
(layer, position); check at least L18 (index 18), ideally all layers:

```python
from safetensors import safe_open
import torch.nn.functional as F

with safe_open("reference_vectors/rollout_160.safetensors",
               framework="pt") as f:
    ref, pos = f.get_tensor("acts"), f.get_tensor("positions")
new = full[:, pos, :]                      # same positions from your run
cos = F.cosine_similarity(new.float(), ref.float(), dim=-1)  # [36, P]
assert cos.min() >= 0.999, cos.min()
```

Rebuild each rollout's `target` from `original_22/texts.jsonl` (match by
`_idx` against `reference_vectors` filenames). If the gate fails at
isolated late-sequence positions with cosine ~0.99x, suspect benign
cross-device numeric drift and report the distribution; if it fails
broadly or at early positions, suspect a token-offset / layer-indexing /
adapter-state mismatch — fix before trusting any regenerated data. Do not
proceed with a failing gate: activations from a wrong pipeline are
worthless (this is the same stop rule used when the archive was created).

## 5. Sanity numbers from the original machine

- Two independent prefills on the source machine agreed to cosine
  >= 0.9999974 at every archived position, all layers (Gate B).
- The oracle probes reproduced the published responses byte-exact
  (156/156, Gate C) — see VERIFICATION_REPORT.md.
- Values are bf16, finite, abs-max ~1.9e4 (Qwen outlier features).
