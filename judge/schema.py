from pydantic import BaseModel, Field
from typing import List

class CriterionVerdict(BaseModel):
    criterion: str
    score: int = Field(ge=1, le=5)
    rationale: str
    evidence: str

class JudgeVerdict(BaseModel):
    winner: str
    criteria: List[CriterionVerdict]
    overall_score_a: float = Field(ge=1, le=5)
    overall_score_b: float = Field(ge=1, le=5)
    overall_rationale: str
