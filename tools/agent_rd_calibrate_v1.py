"""Real-model admission diagnostic, not an experimental research result."""

import json

from agent_rd_admin_v1 import PUBLIC, TASK, write
from agent_rd_remote_v1 import call

schema = {"type": "object", "properties": {"status": {"type": "string", "enum": ["ok"]},
          "value": {"type": "integer"}}, "required": ["status", "value"], "additionalProperties": False}
payload = {"call_id": "admission-format-001", "seed": 17011, "max_tokens": 64, "format": schema,
           "messages": [{"role": "system", "content": "Return one JSON object matching the supplied schema. No prose."},
                        {"role": "user", "content": "Set status to ok and value to the integer 2+2. This checks the local runtime format only."}]}
result = call("infer", payload)
write(TASK / "admission-model-call-v1.json", result, True)
answer = json.loads(result["response"]["message"]["content"])
assert answer == {"status": "ok", "value": 4}
row = result["response"]
receipt = {"status": "PASS_REAL_CPU_ONLY_MODEL_FORMAT_DIAGNOSTIC", "model": result["model"], "model_digest": result["model_digest"],
           "container_cpu_seconds": result["container_cpu_seconds"], "wall_seconds": result["wall_seconds"],
           "prompt_tokens": row.get("prompt_eval_count"), "generated_tokens": row.get("eval_count"),
           "generation_tokens_per_second": row.get("eval_count", 0) / (row.get("eval_duration", 1) / 1e9),
           "research_performance_result": False, "molecular_data_or_hidden_gold_used": False,
           "gpu_vram_bytes": [m["size_vram"] for m in result["running_model_metadata"]["models"]]}
write(PUBLIC / "real-model-format-admission-v1.json", receipt, True)
print(json.dumps(receipt, indent=2))
