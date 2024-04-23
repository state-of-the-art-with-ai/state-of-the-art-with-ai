from typing import Optional
import os

from state_of_the_art.preferences.audience import Audience

class SotaPreferences():
    audiences: dict[str, Audience]

    def __init__(self, *, audiences: Optional[dict[str, Audience]]=None) -> None:
        self.audiences = audiences


    @staticmethod
    def load_preferences() -> None:
        return SotaPreferences()


    def get_current_audience(self=None) -> Audience:

        if not self.audiences:
            return Audience()

        current_profile = os.environ.get('SOTA_PROFILE', 'jean')
        print(f"Using profile {current_profile}")

        return self.audiences[current_profile]
