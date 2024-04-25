from typing import Optional
import os

from state_of_the_art.preferences.audience import Audience

class SotaPreferences():
    audiences: dict[str, Audience]

    def __init__(self, *, audiences: Optional[dict[str, Audience]]=None, default_profile=None) -> None:
        self.audiences = audiences if audiences else {}
        self.default_profile = default_profile

    @staticmethod
    def load_preferences() -> None:
        from examples.preferences import SotaPreferences
        return SotaPreferences()

    def get_current_audience(self=None) -> Audience:
        current_profile = os.environ.get('SOTA_PROFILE', self.default_profile)

        if not current_profile:
            return Audience(name="default")

        if current_profile not in self.audiences:
            raise Exception(f"Profile {current_profile} not found in preferences")

        print(f"Using profile {current_profile}")
        audience = self.audiences[current_profile]
        audience.name = current_profile

        return audience
