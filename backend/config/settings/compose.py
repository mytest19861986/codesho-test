"""Compose settings with the same fail-fast credential validation as production."""

from .local import *  # noqa: F403

from modules.identity.pepper import validate_pepper_settings


validate_pepper_settings(PASSCODE_ACTIVE_PEPPER_ID, PASSCODE_PEPPERS)  # noqa: F405
