from pydantic import BaseModel, validator
from typing import Optional, Literal
from state_of_the_art.config import config


class RecommenderContext(BaseModel):
    by_topic: Optional[str] = None
    lookback_days: Optional[int] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    problem_description: bool = False
    skip_register: bool = False
    dry_run: bool = False
    batch: int = 1
    query: Optional[str] = None
    machine_generated_query: Optional[str] = None
    # if we are receiving in the input  atext with a  list of papers to rank
    papers_to_rank: Optional[str] = None
    batch_size: Optional[int] = config.RANK_MAX_PAPERS_TO_COMPUTE
    number_of_papers_to_recommend: Optional[int] = None
    generated_pdf_location: Optional[str] = None
    type: Optional[Literal["latest", "topic"]] = None

    class Config:
        validate_assignment = True

    @validator("batch_size")
    def set_name(cls, batch_size):
        return batch_size or config.RANK_MAX_PAPERS_TO_COMPUTE
