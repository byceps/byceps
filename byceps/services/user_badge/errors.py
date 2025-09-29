"""
byceps.services.user_badge.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BadgeAwardingFailedError:
    """The awarding of a badge failed."""

    message: str
