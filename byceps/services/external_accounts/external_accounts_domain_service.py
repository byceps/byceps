"""
byceps.services.external_accounts.external_accounts_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .models import ConnectedExternalAccount


def connect_external_account(
    created_at: datetime,
    user: User,
    service: str,
    *,
    external_id: str | None = None,
    external_name: str | None = None,
) -> Result[ConnectedExternalAccount, str]:
    """Connect an external account to a BYCEPS user account."""
    if not external_id and not external_name:
        return Err('Either external ID or external name must be given')

    connected_external_account = ConnectedExternalAccount(
        id=generate_uuid7(),
        created_at=created_at,
        user_id=user.id,
        service=service,
        external_id=external_id,
        external_name=external_name,
    )

    return Ok(connected_external_account)
