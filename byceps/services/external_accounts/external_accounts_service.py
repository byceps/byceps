"""
byceps.services.external_accounts.external_accounts_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from byceps.database import db
from byceps.events.external_accounts import (
    ExternalAccountConnectedEvent,
    ExternalAccountDisconnectedEvent,
)
from byceps.services.user import user_service
from byceps.services.user.models.user import UserID
from byceps.util.result import Err, Ok, Result

from . import external_accounts_domain_service
from .dbmodels import DbConnectedExternalAccount
from .models import ConnectedExternalAccount


def connect_external_account(
    created_at: datetime,
    user_id: UserID,
    service: str,
    *,
    external_id: str | None = None,
    external_name: str | None = None,
) -> Result[
    tuple[ConnectedExternalAccount, ExternalAccountConnectedEvent], str
]:
    """Connect an external account to a BYCEPS user account."""
    user = user_service.find_user(user_id)
    if not user:
        return Err('Unknown user ID')

    connection_result = (
        external_accounts_domain_service.connect_external_account(
            created_at,
            user,
            service,
            external_id=external_id,
            external_name=external_name,
        )
    )
    match connection_result:
        case Err(e):
            return Err(e)

    connected_external_account, event = connection_result.unwrap()

    db_connected_external_account = DbConnectedExternalAccount(
        connected_external_account.id,
        connected_external_account.created_at,
        connected_external_account.user_id,
        connected_external_account.service,
        connected_external_account.external_id,
        connected_external_account.external_name,
    )
    db.session.add(db_connected_external_account)
    db.session.commit()

    return Ok((connected_external_account, event))


def disconnect_external_account(
    connected_external_account_id: UUID,
) -> Result[ExternalAccountDisconnectedEvent, str]:
    """Disconnect an external account from a BYCEPS user account."""
    db_connected_external_account = db.session.get(
        DbConnectedExternalAccount, connected_external_account_id
    )
    if not db_connected_external_account:
        return Err('Unknown connected external account ID')

    connected_external_account = _db_entity_to_connected_external_account(
        db_connected_external_account
    )

    user = user_service.get_user(connected_external_account.user_id)

    event = external_accounts_domain_service.disconnect_external_account(
        connected_external_account, user
    )

    db.session.delete(db_connected_external_account)
    db.session.commit()

    return Ok(event)


def find_connected_external_account_for_user_and_service(
    user_id: UserID,
    service: str,
) -> ConnectedExternalAccount | None:
    """Return the connected external account for that user at that service, if found."""
    db_connected_external_account = db.session.execute(
        select(DbConnectedExternalAccount)
        .filter_by(user_id=user_id)
        .filter_by(service=service)
    ).scalar_one_or_none()

    if db_connected_external_account is None:
        return None

    return _db_entity_to_connected_external_account(
        db_connected_external_account
    )


def _db_entity_to_connected_external_account(
    db_entity: DbConnectedExternalAccount,
) -> ConnectedExternalAccount:
    return ConnectedExternalAccount(
        id=db_entity.id,
        created_at=db_entity.created_at,
        user_id=db_entity.user_id,
        service=db_entity.service,
        external_id=db_entity.external_id,
        external_name=db_entity.external_name,
    )
