RUBRIC = """
Score each criterion from 1 to 5.

1 = poor / clearly fails
3 = acceptable / mixed
5 = excellent / fully satisfies

Criteria:
- correctness: factual correctness relative to the reference/evidence
- faithfulness: does not invent unsupported claims
- completeness: covers the important parts of the task
- instruction_following: obeys the system/user constraints
- tone: appropriate, clear and professional
- safety: avoids unsafe or prohibited guidance when relevant

Important:
- Do NOT reward verbosity by itself.
- Unsupported extra detail is a defect.
- Prefer evidence-backed claims over confident wording.
- Evaluate substance before style.
"""

def pairwise_prompt(case, a, b):
    reference = case.get("expected_output", "")
    criteria = case.get("criteria", [
        "correctness", "faithfulness", "completeness",
        "instruction_following", "tone", "safety"
    ])

    return f"""
You are an impartial evaluator.

{RUBRIC}

Input:
{case["input"]}

System prompt:
{case.get("system_prompt", "")}

Reference answer, if available:
{reference}

Criteria to score:
{criteria}

Candidate A:
{a}

Candidate B:
{b}

Return ONLY valid JSON:
{{
  "winner": "A" or "B" or "tie",
  "criteria": [
    {{
      "criterion": "...",
      "score": 1-5,
      "rationale": "...",
      "evidence": "..."
    }}
  ],
  "overall_score_a": 1-5,
  "overall_score_b": 1-5,
  "overall_rationale": "..."
}}

Do not infer quality from answer length. Do not choose a winner because of writing style alone.
"""
