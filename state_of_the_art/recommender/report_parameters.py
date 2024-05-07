from pydantic import BaseModel, validator
from typing import Optional
from state_of_the_art.config import config


class RecommenderParameters(BaseModel):
    topic_dive: Optional[str] = None
    lookback_days: Optional[int] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    description_from_clipboard: bool = False
    skip_register: bool = False
    dry_run: bool = False
    batch: int = 1
    query: Optional[str] = None
    # if we are receiving in the inpyut  atext with a  list of papers to rank
    papers_to_rank: Optional[str] = None
    batch_size: Optional[int] = config.RANK_MAX_PAPERS_TO_COMPUTE

    class Config:
        validate_assignment = True

    @validator("batch_size")
    def set_name(cls, batch_size):
        return batch_size or config.RANK_MAX_PAPERS_TO_COMPUTE
