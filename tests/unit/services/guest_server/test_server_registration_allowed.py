"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.guest_server import guest_server_domain_service
from byceps.services.guest_server.errors import (
    QuantityLimitReachedError,
    UserUsesNoTicketError,
)
from byceps.util.result import Err, Ok


HAS_TICKET = True
LACKS_TICKET = False

IS_ORGA = True
IS_NOT_ORGA = False

ALLOWED = Ok(None)
DENIED_USER_USES_NO_TICKET = Err(UserUsesNoTicketError())
DENIED_QUANTITY_LIMIT_REACHED = Err(QuantityLimitReachedError())


@pytest.mark.parametrize(
    (
        'user_uses_ticket_for_party',
        'user_is_orga_for_party',
        'already_registered_server_quantity',
        'expected',
    ),
    [
        (LACKS_TICKET, IS_NOT_ORGA, 0, DENIED_USER_USES_NO_TICKET),
        (HAS_TICKET, IS_NOT_ORGA, 0, ALLOWED),
        (LACKS_TICKET, IS_ORGA, 0, ALLOWED),  # orga needs no ticket
        (HAS_TICKET, IS_NOT_ORGA, 4, ALLOWED),
        (HAS_TICKET, IS_NOT_ORGA, 5, DENIED_QUANTITY_LIMIT_REACHED),
        (HAS_TICKET, IS_NOT_ORGA, 6, DENIED_QUANTITY_LIMIT_REACHED),
        (LACKS_TICKET, IS_ORGA, 6, ALLOWED),  # orga may exceed limit
    ],
)
def test_ensure_user_may_register_server(
    user_uses_ticket_for_party: bool,
    user_is_orga_for_party: bool,
    already_registered_server_quantity: int,
    expected: bool,
):
    actual = guest_server_domain_service.ensure_user_may_register_server(
        user_uses_ticket_for_party,
        user_is_orga_for_party,
        already_registered_server_quantity,
    )

    assert actual == expected
