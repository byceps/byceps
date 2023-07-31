"""
byceps.services.authentication.api.authn_api_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.authorization.models import PermissionID
from byceps.typing import UserID

from . import authn_api_domain_service
from .dbmodels import DbApiToken
from .models import ApiToken


def create_api_token(
    creator_id: UserID,
    permissions: set[PermissionID],
    *,
    description: str | None = None,
) -> ApiToken:
    """Create an API token."""
    api_token = authn_api_domain_service.create_api_token(
        creator_id, permissions, description=description
    )

    _persist_api_token(api_token)

    return api_token


def _persist_api_token(api_token: ApiToken) -> None:
    db_api_token = DbApiToken(
        api_token.id,
        api_token.created_at,
        api_token.creator_id,
        api_token.token,
        api_token.permissions,
        api_token.description,
        api_token.suspended,
    )
    db.session.add(db_api_token)
    db.session.commit()


def find_api_token_by_token(token: str) -> ApiToken | None:
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
