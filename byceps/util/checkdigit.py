"""
byceps.util.checkdigit
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import math
from string import ascii_uppercase, digits
from typing import Iterator


VALID_CHARS = frozenset(ascii_uppercase + digits)


def calculate_check_digit(chars: str) -> int:
    """Calculate the check digit for the given value, using a modified
    Luhn algorithm to support not only digits in the value but also
    letters.

    Based on https://wiki.openmrs.org/display/docs/Check+Digit+Algorithm
    """
    chars = chars.strip().upper()

    total_weight = calculate_total_weight(chars)

    # The check digit is the amount needed to reach the next number
    # that is divisible by ten.
    return (10 - (total_weight % 10)) % 10


def calculate_total_weight(chars: str) -> int:
    total_weight = sum(calculate_weights(chars))

    # Avoid a total weight less than 10 (this could happen if
    # characters below `0` are allowed).
    return int(math.fabs(total_weight)) + 10


def calculate_weights(chars: str) -> Iterator[int]:
    # Loop through characters from right to left.
    for position, char in enumerate(reversed(chars)):
        yield calculate_weight(position, char)


def calculate_weight(position: int, char: str) -> int:
    """Calculate the current digit's contribution to the total weight."""
    if char not in VALID_CHARS:
        raise ValueError(f"Invalid character '{char}'.")

    digit = ord(char) - 48
    if is_even(position):
        # This is the same as multiplying by 2 and summing up digits
        # for values 0 to 9. This allows to gracefully calculate the
        # weight for a non-numeric "digit" as well.
        return (2 * digit) - int(digit / 5) * 9
    else:
        return digit


def is_even(n: int) -> bool:
    return n % 2 == 0
