from typing import Optional
import os

from state_of_the_art.preferences.audience import Audience

class SotaPreferences():
    audiences: dict[str, Audience]

    def __init__(self, *, audiences: Optional[dict[str, Audience]]=None) -> None:
        self.audiences = audiences if audiences else {}


    @staticmethod
    def load_preferences() -> None:
        from examples.preferences import SotaPreferences
        return SotaPreferences()


    def get_current_audience(self=None) -> Audience:
        current_profile = os.environ.get('SOTA_PROFILE', None)
        if current_profile and current_profile not in self.audiences:
            raise Exception(f"Profile {current_profile} not found in preferences")

        print(f"Using profile {current_profile}")
        audience = self.audiences[current_profile]
        audience.name = current_profile

        return audience
