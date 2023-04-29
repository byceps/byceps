"""
byceps.services.connected_external_accounts.connected_external_accounts_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from byceps.database import db
from byceps.services.user import user_service
from byceps.typing import UserID
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbConnectedExternalAccount
from .models import ConnectedExternalAccount


def connect_external_account(
    created_at: datetime,
    user_id: UserID,
    service: str,
    *,
    external_id: str | None = None,
    external_name: str | None = None,
) -> Result[ConnectedExternalAccount, str]:
    """Connect a BYCEPS user account to an external account."""
    user = user_service.find_user(user_id)
    if not user:
        return Err('Unknown user ID')

    db_connected_external_account = DbConnectedExternalAccount(
        created_at,
        user_id,
        service,
        external_id=external_id,
        external_name=external_name,
    )
    db.session.add(db_connected_external_account)
    db.session.commit()

    connected_external_account = _db_entity_to_connected_external_account(
        db_connected_external_account
    )

    return Ok(connected_external_account)


def disconnect_external_account(
    connected_external_account_id: UUID,
) -> Result[None, str]:
    """Connect a BYCEPS user account from an external account."""
    db_connected_external_account = db.session.get(
        DbConnectedExternalAccount, connected_external_account_id
    )
    if not db_connected_external_account:
        return Err('Unknown connected external account ID')

    db.session.delete(db_connected_external_account)
    db.session.commit()

    return Ok(None)


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
