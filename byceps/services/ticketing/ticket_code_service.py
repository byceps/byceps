"""
byceps.services.ticketing.ticket_code_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from random import sample
from typing import Set

from .transfer.models import TicketCode


def generate_ticket_codes(quantity: int) -> Set[TicketCode]:
    """Generate a number of ticket codes."""
    codes: Set[TicketCode] = set()

    for _ in range(quantity):
        code = _generate_ticket_code_not_in(codes)
        codes.add(code)

    # Check if the correct number of codes has been generated.
    _verify_total_matches(codes, quantity)

    return codes


def _generate_ticket_code_not_in(
    codes: Set[TicketCode], *, max_attempts: int = 4
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
    codes: Set[TicketCode], requested_quantity: int
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
