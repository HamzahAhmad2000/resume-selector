from pydantic import BaseModel
from typing import List


class JobPayload(BaseModel):
    title: str
    description: str


class FeedbackPayload(BaseModel):
    job_id: int
    shown_candidate_ids: List[int]
    chosen_candidate_id: int
