"""
byceps.services.authentication.api.authn_api_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from secrets import token_urlsafe
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.authorization.models import PermissionID
from byceps.typing import UserID

from .dbmodels import DbApiToken
from .models import ApiToken


def create_api_token(
    creator_id: UserID,
    permissions: set[PermissionID],
    *,
    description: Optional[str] = None,
) -> ApiToken:
    """Create an API token."""
    num_bytes = 40
    token = token_urlsafe(num_bytes)

    db_api_token = DbApiToken(
        creator_id, token, permissions, description=description
    )
    db.session.add(db_api_token)
    db.session.commit()

    return _db_entity_to_api_token(db_api_token)


def find_api_token_by_token(token: str) -> Optional[ApiToken]:
    """Return the API token for that token, or nothing if not found."""
    db_api_token = db.session.execute(
        select(DbApiToken).filter_by(token=token)
    ).scalar_one_or_none()

    if db_api_token is None:
        return None

    return _db_entity_to_api_token(db_api_token)


def get_all_api_tokens() -> list[ApiToken]:
    """Return all API tokens."""
    db_api_tokens = db.session.scalars(select(DbApiToken)).unique().all()

    return [
        _db_entity_to_api_token(db_api_token) for db_api_token in db_api_tokens
    ]


def suspend_api_token(api_token_id: UUID) -> None:
    """Suspend the API token."""
    db_api_token = _get_db_api_token(api_token_id)
    db_api_token.suspended = True
    db.session.commit()


def unsuspend_api_token(api_token_id: UUID) -> None:
    """Unsuspend the API token."""
    db_api_token = _get_db_api_token(api_token_id)
    db_api_token.suspended = False
    db.session.commit()


def _get_db_api_token(api_token_id: UUID) -> DbApiToken:
    db_api_token = db.session.get(DbApiToken, api_token_id)

    if db_api_token is None:
        raise ValueError(f"Unknown API token '{api_token_id}'")

    return db_api_token


def delete_api_token(api_token_id: UUID) -> None:
    """Delete the API token."""
    db.session.execute(
        delete(DbApiToken)
        .where(DbApiToken.id == api_token_id)
        .execution_options(synchronize_session='fetch')
    )
    db.session.commit()


def _db_entity_to_api_token(db_api_token: DbApiToken) -> ApiToken:
    return ApiToken(
        id=db_api_token.id,
        created_at=db_api_token.created_at,
        creator_id=db_api_token.creator_id,
        token=db_api_token.token,
        permissions=frozenset(db_api_token.permissions),
        description=db_api_token.description,
        suspended=db_api_token.suspended,
    )
