"""Versioned workspace-only contract; never imported by research runners."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FollowupPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    answer_status: Literal["reported", "explicit_negative", "unknown", "unanswered"]
    evidence: str = Field(max_length=1000)
    relevant_new_information: bool
    missing_key: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    missing_information: str = Field(min_length=1, max_length=250)
    question: str = Field(min_length=5, max_length=250)
    options: list[str] = Field(min_length=2, max_length=4)
    selection_reason: Literal["urgency_discriminator", "clarify_report", "new_information"]

    @model_validator(mode="after")
    def one_question(self):
        if self.question.count("?") != 1 or not self.question.endswith("?"):
            raise ValueError("Exactly one question required")
        if len(set(self.options)) != len(self.options) or any(not x.strip() or len(x) > 150 for x in self.options):
            raise ValueError("Options must be distinct short answers")
        if self.answer_status in {"reported", "explicit_negative"} and not self.evidence:
            raise ValueError("An observed fact needs a verbatim evidence quote")
        return self
