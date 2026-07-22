"""Compose settings with the same fail-fast credential validation as production."""

from modules.identity.pepper import validate_pepper_settings

from .local import *  # noqa: F403

validate_pepper_settings(PASSCODE_ACTIVE_PEPPER_ID, PASSCODE_PEPPERS)  # noqa: F405
