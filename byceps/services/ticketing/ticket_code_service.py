"""
byceps.services.ticketing.ticket_code_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from random import sample
from string import ascii_uppercase, digits

from byceps.util.result import Err, Ok, Result

from .models.ticket import TicketCode


def generate_ticket_codes(
    requested_quantity: int,
) -> Result[set[TicketCode], str]:
    """Generate a number of ticket codes."""
    codes: set[TicketCode] = set()

    for _ in range(requested_quantity):
        generation_result = _generate_ticket_code_not_in(codes)

        if generation_result.is_err():
            return Err(generation_result.unwrap_err())

        code = generation_result.unwrap()
        codes.add(code)

    # Check if the requested quantity of codes has been generated.
    actual_quantity = len(codes)
    if actual_quantity != requested_quantity:
        return Err(
            f'Number of generated ticket codes ({actual_quantity}) '
            f'does not match requested quantity ({requested_quantity}).'
        )

    return Ok(codes)


def _generate_ticket_code_not_in(
    codes: set[TicketCode], *, max_attempts: int = 4
) -> Result[TicketCode, str]:
    """Generate ticket codes and return the first one not in the set."""
    for _ in range(max_attempts):
        code = _generate_ticket_code()
        if code not in codes:
            return Ok(code)

    return Err(
        f'Could not generate unique ticket code after {max_attempts} attempts.'
    )


_CODE_ALPHABET = 'BCDFGHJKLMNPQRSTVWXYZ'
_CODE_LENGTH = 5


def _generate_ticket_code() -> TicketCode:
    """Generate a ticket code.

    Generated codes are not necessarily unique!
    """
    return TicketCode(''.join(sample(_CODE_ALPHABET, _CODE_LENGTH)))


_ALLOWED_CODE_SYMBOLS = frozenset(_CODE_ALPHABET + ascii_uppercase + digits)


def is_ticket_code_wellformed(code: str) -> bool:
    """Determine if the ticket code is well-formed."""
    return len(code) == _CODE_LENGTH and set(code).issubset(
        _ALLOWED_CODE_SYMBOLS
    )
