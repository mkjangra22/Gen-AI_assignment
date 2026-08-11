import json
from pathlib import Path

from rag.config import settings
from rag.llm import LLMClient, parse_json_robust
from .prompts import pairwise_prompt
from .schema import JudgeVerdict

class JudgeRunner:
    def __init__(self):
        self.client = LLMClient(
            settings.judge_base_url,
            settings.judge_api_key,
            settings.judge_model,
            settings.judge_temperature,
        )

    def judge_pair(self, case, a, b, order="AB"):
        if order == "AB":
            prompt = pairwise_prompt(case, a, b)
        else:
            prompt = pairwise_prompt(case, b, a)

        raw = None
        error = None

        try:
            response = self.client.chat(
                [{"role": "user", "content": prompt}],
                json_mode=True,
            )
            raw = response
            data = parse_json_robust(response["text"])
            verdict = JudgeVerdict.model_validate(data)
            return {
                "ok": True,
                "order": order,
                "prompt": prompt,
                "verdict": verdict.model_dump(),
                "raw_response": response["text"],
                "usage": {
                    "prompt_tokens": response["prompt_tokens"],
                    "completion_tokens": response["completion_tokens"],
                    "total_tokens": response["total_tokens"],
                    "latency_ms": response["latency_ms"],
                },
            }
        except Exception as exc:
            error = str(exc)

        # One repair attempt.
        if raw is not None:
            try:
                repair = self.client.chat([
                    {
                        "role": "user",
                        "content": (
                            "Repair the following into ONLY valid JSON matching "
                            "the requested schema. Do not change the meaning.\n\n"
                            + raw["text"]
                        ),
                    }
                ], json_mode=True)
                data = parse_json_robust(repair["text"])
                verdict = JudgeVerdict.model_validate(data)
                return {
                    "ok": True,
                    "order": order,
                    "prompt": prompt,
                    "repair_prompt": (
                        "Repair the following into ONLY valid JSON matching "
                        "the requested schema. Do not change the meaning.\n\n"
                        + raw["text"]
                    ),
                    "repaired": True,
                    "verdict": verdict.model_dump(),
                    "raw_response": repair["text"],
                    "usage": {
                        "prompt_tokens": repair["prompt_tokens"],
                        "completion_tokens": repair["completion_tokens"],
                        "total_tokens": repair["total_tokens"],
                        "latency_ms": repair["latency_ms"],
                    },
                }
            except Exception as exc2:
                error = f"{error}; repair failed: {exc2}"

        return {"ok": False, "order": order, "error": error}

    def audit_log(self, record, path="results/judge_raw.jsonl"):
        Path(path).parent.mkdir(exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
