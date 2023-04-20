"""
byceps.services.user.screen_name_validator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validate screen names regarding their contained characters

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from itertools import chain
from string import ascii_letters, digits


MIN_LENGTH = 3
MAX_LENGTH = 24

GERMAN_CHARS = 'äöüß'
SPECIAL_CHARS = '!$*-./<=>[]_'

# The at sign (`@`) is not allowed in the screen name because it is
# used to distinguish a screen name from an e-mail address on login.

VALID_CHARS = frozenset(
    chain(ascii_letters, digits, GERMAN_CHARS, SPECIAL_CHARS)
)


def is_screen_name_valid(screen_name: str) -> bool:
    """Return `True` if the screen name has a valid length and contains
    only permitted characters.
    """
    return is_length_valid(screen_name) and contains_only_valid_chars(
        screen_name
    )


def is_length_valid(screen_name: str) -> bool:
    """Return `True` if the screen name has a valid length."""
    return MIN_LENGTH <= len(screen_name) <= MAX_LENGTH


def contains_only_valid_chars(screen_name: str) -> bool:
    """Return `True` if the screen name contains only permitted characters."""
    return all(map(VALID_CHARS.__contains__, screen_name))
