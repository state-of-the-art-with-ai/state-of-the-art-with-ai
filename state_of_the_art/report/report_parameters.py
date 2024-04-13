
from pydantic import BaseModel
from typing import Optional

class ReportParemeters(BaseModel):
    lookback_days:Optional[int]=None
    from_date:Optional[str]=None
    to_date:Optional[str]=None
    skip_register:bool=False
    dry_run:bool=False
    batch: int =1