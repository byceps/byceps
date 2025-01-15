"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

import pytest

from byceps.services.guest_server import guest_server_domain_service
from byceps.services.guest_server.errors import (
    PartyIsOverError,
    QuantityLimitReachedError,
    UserUsesNoTicketError,
)
from byceps.services.party.models import Party
from byceps.util.result import Err, Ok


@dataclass(frozen=True)
class PartyOver:
    is_over: bool = True


@dataclass(frozen=True)
class PartyNotOver:
    is_over: bool = False


PARTY_NOT_OVER = PartyNotOver()
PARTY_OVER = PartyOver()

HAS_TICKET = True
LACKS_TICKET = False

IS_ORGA = True
IS_NOT_ORGA = False

ALLOWED = Ok(None)
DENIED_USER_USES_NO_TICKET = Err(UserUsesNoTicketError())
DENIED_QUANTITY_LIMIT_REACHED = Err(QuantityLimitReachedError())
DENIED_PARTY_IS_OVER = Err(PartyIsOverError())


@pytest.mark.parametrize(
    (
        'party',
        'user_uses_ticket_for_party',
        'user_is_orga_for_party',
        'already_registered_server_quantity',
        'expected',
    ),
    [
        (
            PARTY_NOT_OVER,
            LACKS_TICKET,
            IS_NOT_ORGA,
            0,
            DENIED_USER_USES_NO_TICKET,
        ),
        (
            PARTY_OVER,
            LACKS_TICKET,
            IS_NOT_ORGA,
            0,
            DENIED_PARTY_IS_OVER,
        ),
        (
            PARTY_OVER,
            HAS_TICKET,
            IS_NOT_ORGA,
            0,
            DENIED_PARTY_IS_OVER,
        ),
        (
            PARTY_OVER,
            LACKS_TICKET,
            IS_ORGA,
            0,
            DENIED_PARTY_IS_OVER,
        ),
        (
            PARTY_NOT_OVER,
            HAS_TICKET,
            IS_NOT_ORGA,
            0,
            ALLOWED,
        ),
        (  # orga needs no ticket
            PARTY_NOT_OVER,
            LACKS_TICKET,
            IS_ORGA,
            0,
            ALLOWED,
        ),
        (
            PARTY_NOT_OVER,
            HAS_TICKET,
            IS_NOT_ORGA,
            4,
            ALLOWED,
        ),
        (
            PARTY_NOT_OVER,
            HAS_TICKET,
            IS_NOT_ORGA,
            5,
            DENIED_QUANTITY_LIMIT_REACHED,
        ),
        (
            PARTY_NOT_OVER,
            HAS_TICKET,
            IS_NOT_ORGA,
            6,
            DENIED_QUANTITY_LIMIT_REACHED,
        ),
        (  # orga may exceed limit
            PARTY_NOT_OVER,
            LACKS_TICKET,
            IS_ORGA,
            6,
            ALLOWED,
        ),
    ],
)
def test_ensure_user_may_register_server(
    party: Party,
    user_uses_ticket_for_party: bool,
    user_is_orga_for_party: bool,
    already_registered_server_quantity: int,
    expected: bool,
):
    actual = guest_server_domain_service.ensure_user_may_register_server(
        party,
        user_uses_ticket_for_party,
        user_is_orga_for_party,
        already_registered_server_quantity,
    )

    assert actual == expected
