"""
byceps.services.email.email_config_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from byceps.database import db, upsert
from byceps.typing import BrandID
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbEmailConfig
from .models import EmailConfig, NameAndAddress


class UnknownEmailConfigIdError(ValueError):
    pass


def create_config(
    brand_id: BrandID,
    sender_address: str,
    *,
    sender_name: str | None = None,
    contact_address: str | None = None,
) -> EmailConfig:
    """Create a configuration."""
    db_config = DbEmailConfig(
        brand_id,
        sender_address,
        sender_name=sender_name,
        contact_address=contact_address,
    )

    db.session.add(db_config)
    db.session.commit()

    return _db_entity_to_config(db_config)


def update_config(
    brand_id: BrandID,
    sender_address: str,
    sender_name: str | None,
    contact_address: str | None,
) -> Result[EmailConfig, str]:
    """Update a configuration."""
    db_config = _find_db_config(brand_id)

    if db_config is None:
        return Err(f'No e-mail config found for brand ID "{brand_id}"')

    db_config.sender_address = sender_address
    db_config.sender_name = sender_name
    db_config.contact_address = contact_address

    db.session.commit()

    config = _db_entity_to_config(db_config)

    return Ok(config)


def delete_config(brand_id: BrandID) -> bool:
    """Delete a configuration.

    It is expected that no database records (sites) refer to the
    configuration anymore.

    Return `True` on success, or `False` if an error occurred.
    """
    get_config(brand_id)  # Verify ID exists.

    try:
        db.session.execute(
            delete(DbEmailConfig).where(DbEmailConfig.brand_id == brand_id)
        )

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False

    return True


def _find_db_config(brand_id: BrandID) -> DbEmailConfig | None:
    return db.session.scalars(
        select(DbEmailConfig).filter_by(brand_id=brand_id)
    ).one_or_none()


def get_config(brand_id: BrandID) -> EmailConfig:
    """Return the configuration, or raise an error if none is configured
    for that brand.
    """
    db_config = _find_db_config(brand_id)

    if db_config is None:
        raise UnknownEmailConfigIdError(
            f'No e-mail config found for brand ID "{brand_id}"'
        )

    return _db_entity_to_config(db_config)


def set_config(
    brand_id: BrandID,
    sender_address: str,
    *,
    sender_name: str | None = None,
    contact_address: str | None = None,
) -> None:
    """Add or update configuration for that ID."""
    table = DbEmailConfig.__table__
    identifier = {
        'brand_id': brand_id,
        'sender_address': sender_address,
    }
    replacement = {
        'sender_name': sender_name,
        'contact_address': contact_address,
    }

    upsert(table, identifier, replacement)


def get_all_configs() -> list[EmailConfig]:
    """Return all configurations."""
    db_configs = db.session.scalars(select(DbEmailConfig)).all()

    return [_db_entity_to_config(db_config) for db_config in db_configs]


def _db_entity_to_config(db_config: DbEmailConfig) -> EmailConfig:
    sender = NameAndAddress(
        name=db_config.sender_name,
        address=db_config.sender_address,
    )

    return EmailConfig(
        brand_id=db_config.brand_id,
        sender=sender,
        contact_address=db_config.contact_address,
    )
