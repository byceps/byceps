"""
byceps.services.webhooks.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any, Optional

from sqlalchemy.ext.mutable import MutableDict

from ...database import db, generate_uuid

from .transfer.models import EventFilters, EventSelectors


class OutgoingWebhook(db.Model):
    """An outgoing webhook configuration."""

    __tablename__ = 'outgoing_webhooks'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    event_selectors = db.Column(MutableDict.as_mutable(db.JSONB), nullable=True)
    event_filters = db.Column(MutableDict.as_mutable(db.JSONB), nullable=True)
    format = db.Column(db.UnicodeText, nullable=False)
    text_prefix = db.Column(db.UnicodeText, nullable=True)
    extra_fields = db.Column(MutableDict.as_mutable(db.JSONB), nullable=True)
    url = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    enabled = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        event_selectors: EventSelectors,
        event_filters: EventFilters,
        format: str,
        url: str,
        enabled: bool,
        *,
        text_prefix: Optional[str] = None,
        extra_fields: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> None:
        self.event_selectors = event_selectors
        self.event_filters = event_filters
        self.format = format
        self.text_prefix = text_prefix
        self.extra_fields = extra_fields
        self.url = url
        self.description = description
        self.enabled = enabled
