from typing import Any, List, Optional
import os

from state_of_the_art.preferences.audience import Audience

class SotaPreferences():
    audiences: dict[str, Audience]
    keywords: List[str]
    keywords_to_exclude: List[str]
    time_frame: Any = None
    paper_tasks: Optional[dict] = None

    def __init__(self, *, audiences: Optional[dict[str, Audience]]=None, paper_tasks=None) -> None:
        self.audiences = audiences
        self.paper_tasks = paper_tasks


    @staticmethod
    def load_preferences() -> None:
        return SotaPreferences()


    def get_current_audience(self=None) -> Audience:

        if not self.audiences:
            return Audience()

        current_profile = os.environ.get('SOTA_PROFILE', 'jean')
        print(f"Using profile {current_profile}")

        return self.audiences[current_profile]
