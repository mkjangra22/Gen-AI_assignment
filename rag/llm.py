import json
import time
import requests

class LLMClient:
    def __init__(self, base_url, api_key, model, temperature=0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def chat(self, messages, json_mode=False):
        if not self.api_key or not self.model:
            raise RuntimeError(
                "LLM is not configured. Set LLM_API_KEY and LLM_MODEL in .env."
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        started = time.perf_counter()
        for attempt in range(4):
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=90,
            )
            if response.status_code == 429 and attempt < 3:
                time.sleep(12 * (attempt + 1))
                continue
            response.raise_for_status()
            break
        latency_ms = (time.perf_counter() - started) * 1000
        data = response.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return {
            "text": choice,
            "latency_ms": latency_ms,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "raw": data,
        }

def parse_json_robust(text: str):
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Remove common markdown fences.
    cleaned = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        return json.loads(cleaned[start:end + 1])

    raise ValueError("Could not parse a JSON object from judge response.")
