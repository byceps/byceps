"""
byceps.services.external_accounts.external_accounts_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .events import (
    ExternalAccountConnectedEvent,
    ExternalAccountDisconnectedEvent,
)
from .models import ConnectedExternalAccount


def connect_external_account(
    created_at: datetime,
    user: User,
    service: str,
    *,
    external_id: str | None = None,
    external_name: str | None = None,
) -> Result[
    tuple[ConnectedExternalAccount, ExternalAccountConnectedEvent], str
]:
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

    event = _build_external_account_connected_event(
        connected_external_account, user
    )

    return Ok((connected_external_account, event))


def _build_external_account_connected_event(
    connected_external_account: ConnectedExternalAccount, user: User
) -> ExternalAccountConnectedEvent:
    return ExternalAccountConnectedEvent(
        connected_external_account_id=connected_external_account.id,
        occurred_at=connected_external_account.created_at,
        initiator=user,
        user=user,
        service=connected_external_account.service,
        external_id=connected_external_account.external_id,
        external_name=connected_external_account.external_name,
    )


def disconnect_external_account(
    connected_external_account: ConnectedExternalAccount, user: User
) -> ExternalAccountDisconnectedEvent:
    """Disonnect a BYCEPS user account from an external account."""
    event = _build_external_account_disconnected_event(
        connected_external_account, user
    )

    return event


def _build_external_account_disconnected_event(
    connected_external_account: ConnectedExternalAccount, user: User
) -> ExternalAccountDisconnectedEvent:
    return ExternalAccountDisconnectedEvent(
        connected_external_account_id=connected_external_account.id,
        occurred_at=connected_external_account.created_at,
        initiator=user,
        user=user,
        service=connected_external_account.service,
        external_id=connected_external_account.external_id,
        external_name=connected_external_account.external_name,
    )
