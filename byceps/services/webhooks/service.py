"""
byceps.services.webhooks.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Set

from ...database import db

from .models import OutgoingWebhook as DbOutgoingWebhook
from .transfer.models import OutgoingWebhook, WebhookID


def create_outgoing_webhook(
    scope: str,
    scope_id: Optional[str],
    format: str,
    url: str,
    enabled: bool,
    *,
    text_prefix: Optional[str] = None,
) -> OutgoingWebhook:
    """Create an outgoing webhook."""
    webhook = DbOutgoingWebhook(
        scope, scope_id, format, url, enabled, text_prefix=text_prefix
    )

    db.session.add(webhook)
    db.session.commit()

    return _db_entity_to_outgoing_webhook(webhook)


def delete_outgoing_webhook(webhook_id: WebhookID) -> None:
    """Delete the outgoing webhook."""
    db.session.query(DbOutgoingWebhook) \
        .filter_by(id=webhook_id) \
        .delete()
    db.session.commit()


def find_enabled_outgoing_webhook(
    scope: str, scope_id: str, format: str
) -> Optional[OutgoingWebhook]:
    """Return the configuration for an enabled outgoing webhook with the
    given scope and format.
    """
    webhook = db.session.query(DbOutgoingWebhook) \
        .filter_by(scope=scope) \
        .filter_by(scope_id=scope_id) \
        .filter_by(format=format) \
        .one_or_none()

    if webhook is None:
        return None

    return _db_entity_to_outgoing_webhook(webhook)


def _db_entity_to_outgoing_webhook(
    webhook: DbOutgoingWebhook,
) -> OutgoingWebhook:
    return OutgoingWebhook(
        webhook.id,
        webhook.scope,
        webhook.scope_id,
        webhook.format,
        webhook.text_prefix,
        webhook.url,
        webhook.enabled,
    )
