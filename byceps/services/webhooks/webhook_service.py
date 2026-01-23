"""
byceps.services.webhooks.webhook_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any

from sqlalchemy import delete, select

from byceps.database import db
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid4

from .dbmodels import DbOutgoingWebhook
from .models import (
    EventFilters,
    OutgoingWebhook,
    OutgoingWebhookFormat,
    WebhookID,
)


def create_outgoing_webhook(
    event_types: set[str],
    event_filters: EventFilters,
    format: OutgoingWebhookFormat,
    url: str,
    enabled: bool,
    *,
    text_prefix: str | None = None,
    extra_fields: dict[str, Any] | None = None,
    description: str | None = None,
) -> OutgoingWebhook:
    """Create an outgoing webhook."""
    webhook_id = WebhookID(generate_uuid4())

    db_webhook = DbOutgoingWebhook(
        webhook_id,
        event_types,
        event_filters,
        format,
        url,
        enabled,
        text_prefix=text_prefix,
        extra_fields=extra_fields,
        description=description,
    )

    db.session.add(db_webhook)
    db.session.commit()

    return _db_entity_to_outgoing_webhook(db_webhook)


def update_outgoing_webhook(
    webhook_id: WebhookID,
    event_types: set[str],
    event_filters: EventFilters,
    format: OutgoingWebhookFormat,
    text_prefix: str | None,
    extra_fields: dict[str, Any] | None,
    url: str,
    description: str | None,
    enabled: bool,
) -> Result[OutgoingWebhook, str]:
    """Update an outgoing webhook."""
    db_webhook = _find_db_webhook(webhook_id)
    if db_webhook is None:
        return Err(f'Unknown webhook ID "{webhook_id}"')

    db_webhook.event_types = event_types
    db_webhook.event_filters = event_filters
    db_webhook.format = format
    db_webhook.text_prefix = text_prefix
    db_webhook.extra_fields = extra_fields
    db_webhook.url = url
    db_webhook.description = description
    db_webhook.enabled = enabled

    db.session.commit()

    return Ok(_db_entity_to_outgoing_webhook(db_webhook))


def delete_outgoing_webhook(webhook_id: WebhookID) -> None:
    """Delete the outgoing webhook."""
    db.session.execute(
        delete(DbOutgoingWebhook).where(DbOutgoingWebhook.id == webhook_id)
    )
    db.session.commit()


def find_webhook(webhook_id: WebhookID) -> OutgoingWebhook | None:
    """Return the webhook with that ID, if found."""
    db_webhook = _find_db_webhook(webhook_id)

    if db_webhook is None:
        return None

    return _db_entity_to_outgoing_webhook(db_webhook)


def _find_db_webhook(webhook_id: WebhookID) -> DbOutgoingWebhook | None:
    """Return the webhook database entity with that ID, if found."""
    return db.session.get(DbOutgoingWebhook, webhook_id)


def get_all_webhooks() -> list[OutgoingWebhook]:
    """Return all webhooks."""
    db_webhooks = db.session.scalars(select(DbOutgoingWebhook)).all()

    return [
        _db_entity_to_outgoing_webhook(db_webhook) for db_webhook in db_webhooks
    ]


def get_enabled_outgoing_webhooks(event_type: str) -> list[OutgoingWebhook]:
    """Return the configurations for enabled outgoing webhooks for that
    event type.
    """
    db_webhooks = db.session.scalars(
        select(DbOutgoingWebhook)
        .filter(DbOutgoingWebhook._event_types.contains([event_type]))
        .filter_by(enabled=True)
    ).all()

    return [
        _db_entity_to_outgoing_webhook(db_webhook) for db_webhook in db_webhooks
    ]


def _db_entity_to_outgoing_webhook(
    db_webhook: DbOutgoingWebhook,
) -> OutgoingWebhook:
    event_filters = (
        dict(db_webhook.event_filters)
        if (db_webhook.event_filters is not None)
        else {}
    )

    extra_fields = (
        dict(db_webhook.extra_fields)
        if (db_webhook.extra_fields is not None)
        else {}
    )

    return OutgoingWebhook(
        id=db_webhook.id,
        event_types=db_webhook.event_types,
        event_filters=event_filters,
        format=db_webhook.format,
        text_prefix=db_webhook.text_prefix,
        extra_fields=extra_fields,
        url=db_webhook.url,
        description=db_webhook.description,
        enabled=db_webhook.enabled,
    )
