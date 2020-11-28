"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from ...database import db, upsert
from ... import email
from ...typing import BrandID
from ...util.jobqueue import enqueue

from .models import EmailConfig as DbEmailConfig
from .transfer.models import EmailConfig, Message, Sender


class UnknownEmailConfigId(ValueError):
    pass


def create_config(
    config_id: str,
    brand_id: BrandID,
    sender_address: str,
    *,
    sender_name: Optional[str] = None,
    contact_address: Optional[str] = None,
) -> EmailConfig:
    """Create a configuration."""
    config = DbEmailConfig(
        config_id,
        brand_id,
        sender_address,
        sender_name=sender_name,
        contact_address=contact_address,
    )

    db.session.add(config)
    db.session.commit()

    return _db_entity_to_config(config)


def update_config(
    config_id: str,
    sender_address: str,
    sender_name: Optional[str],
    contact_address: Optional[str],
) -> EmailConfig:
    """Update a configuration."""
    config = DbEmailConfig.query.get(config_id)

    if config is None:
        raise UnknownEmailConfigId(config_id)

    config.sender_address = sender_address
    config.sender_name = sender_name
    config.contact_address = contact_address

    db.session.commit()

    return _db_entity_to_config(config)


def delete_config(config_id: str) -> bool:
    """Delete a configuration.

    It is expected that no database records (sites) refer to the
    configuration anymore.

    Return `True` on success, or `False` if an error occurred.
    """
    get_config(config_id)  # Verify ID exists.

    try:
        db.session.query(DbEmailConfig) \
            .filter_by(id=config_id) \
            .delete()

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False

    return True


def find_config(config_id: str) -> Optional[EmailConfig]:
    """Return the configuration, or `None` if not found."""
    config = DbEmailConfig.query.get(config_id)

    if config is None:
        return None

    return _db_entity_to_config(config)


def get_config(config_id: str) -> EmailConfig:
    """Return the configuration, or raise an error if none is
    configured for that ID.
    """
    config = find_config(config_id)

    if not config:
        raise UnknownEmailConfigId(f'Unknown e-mail config ID "{config_id}"')

    return config


def find_config_for_brand(brand_id: BrandID) -> Optional[EmailConfig]:
    """Return the configuration for that brand, or `None` if not found."""
    config = DbEmailConfig.query \
        .filter_by(brand_id=brand_id) \
        .one_or_none()

    if config is None:
        return None

    return _db_entity_to_config(config)


def get_config_for_brand(brand_id: BrandID) -> EmailConfig:
    """Return the configuration for that brand, or raise an error if
    none is configured for that brand ID.
    """
    config = find_config_for_brand(brand_id)

    if config is None:
        raise UnknownEmailConfigId(
            f'No e-mail config found for brand ID "{brand_id}"'
        )

    return config


def set_config(
    config_id: str,
    brand_id: BrandID,
    sender_address: str,
    *,
    sender_name: Optional[str] = None,
    contact_address: Optional[str] = None,
) -> None:
    """Add or update configuration for that ID."""
    table = DbEmailConfig.__table__
    identifier = {
        'id': config_id,
        'brand_id': brand_id,
        'sender_address': sender_address,
    }
    replacement = {
        'sender_name': sender_name,
        'contact_address': contact_address,
    }

    upsert(table, identifier, replacement)


def get_all_configs() -> List[EmailConfig]:
    """Return all configurations."""
    configs = DbEmailConfig.query.all()

    return [_db_entity_to_config(config) for config in configs]


def enqueue_message(message: Message) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    enqueue_email(
        message.sender, message.recipients, message.subject, message.body
    )


def enqueue_email(
    sender: Optional[Sender], recipients: List[str], subject: str, body: str
) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    sender_str = sender.format() if (sender is not None) else None

    enqueue(send_email, sender_str, recipients, subject, body)


def send_email(
    sender: Optional[str], recipients: List[str], subject: str, body: str
) -> None:
    """Send e-mail."""
    email.send(sender, recipients, subject, body)


def _db_entity_to_config(config: DbEmailConfig) -> EmailConfig:
    sender = Sender(
        config.sender_address,
        config.sender_name,
    )

    return EmailConfig(
        config.id,
        config.brand_id,
        sender,
        config.contact_address,
    )
