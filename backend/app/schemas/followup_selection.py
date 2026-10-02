"""LLM selects an observation; wording/options belong to a stable contract."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class FollowupSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    answer_status: Literal["reported", "explicit_negative", "unknown", "unanswered"]
    evidence: str = Field(max_length=1000)
    relevant_new_information: bool
    missing_key: Literal[
        "urine_output", "breathing_effort", "responsiveness", "appetite",
        "vomiting_frequency", "abdomen_size", "stool", "mobility", "pain",
        "bleeding_amount", "discharge", "eye_opening", "onset", "exposure",
        "gum_color", "water_intake", "none",
    ]
    selection_reason: Literal["urgency_discriminator", "clarify_report", "new_information"]
