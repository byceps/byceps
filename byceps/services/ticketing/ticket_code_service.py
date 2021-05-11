"""
byceps.services.ticketing.ticket_code_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from random import sample
from string import ascii_uppercase, digits

from .transfer.models import TicketCode


def generate_ticket_codes(quantity: int) -> set[TicketCode]:
    """Generate a number of ticket codes."""
    codes: set[TicketCode] = set()

    for _ in range(quantity):
        code = _generate_ticket_code_not_in(codes)
        codes.add(code)

    # Check if the correct number of codes has been generated.
    _verify_total_matches(codes, quantity)

    return codes


def _generate_ticket_code_not_in(
    codes: set[TicketCode], *, max_attempts: int = 4
) -> TicketCode:
    """Generate ticket codes and return the first one not in the set."""
    for _ in range(max_attempts):
        code = _generate_ticket_code()
        if code not in codes:
            return code

    raise TicketCodeGenerationFailed(
        f'Could not generate unique ticket code after {max_attempts} attempts.'
    )


_CODE_ALPHABET = 'BCDFGHJKLMNPQRSTVWXYZ'
_CODE_LENGTH = 5


def _generate_ticket_code() -> TicketCode:
    """Generate a ticket code.

    Generated codes are not necessarily unique!
    """
    return TicketCode(''.join(sample(_CODE_ALPHABET, _CODE_LENGTH)))


def _verify_total_matches(
    codes: set[TicketCode], requested_quantity: int
) -> None:
    """Verify if the number of generated codes matches the number of
    requested codes.

    Raise an exception if they do not match.
    """
    actual_quantity = len(codes)
    if actual_quantity != requested_quantity:
        raise TicketCodeGenerationFailed(
            f'Number of generated ticket codes ({actual_quantity}) '
            f'does not match requested amount ({requested_quantity}).'
        )


class TicketCodeGenerationFailed(Exception):
    """Generating one or more unique ticket codes has failed."""


_ALLOWED_CODE_SYMBOLS = frozenset(_CODE_ALPHABET + ascii_uppercase + digits)


def is_ticket_code_wellformed(code: str) -> bool:
    """Determine if the ticket code is well-formed."""
    return len(code) == _CODE_LENGTH and set(code).issubset(_ALLOWED_CODE_SYMBOLS)
