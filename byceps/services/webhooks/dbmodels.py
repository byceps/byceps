"""
byceps.services.webhooks.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict, MutableList

from byceps.database import db
from byceps.util.uuid import generate_uuid4

from .models import EventFilters, OutgoingWebhookFormat, WebhookID


class DbOutgoingWebhook(db.Model):
    """An outgoing webhook configuration."""

    __tablename__ = 'outgoing_webhooks'

    id: Mapped[WebhookID] = mapped_column(
        db.Uuid, default=generate_uuid4, primary_key=True
    )
    _event_types: Mapped[list[str]] = mapped_column(
        'event_types', MutableList.as_mutable(db.JSONB)
    )
    event_filters: Mapped[Any | None] = mapped_column(
        MutableDict.as_mutable(db.JSONB)
    )
    _format: Mapped[str] = mapped_column('format', db.UnicodeText)
    text_prefix: Mapped[str | None] = mapped_column(db.UnicodeText)
    extra_fields: Mapped[Any | None] = mapped_column(
        MutableDict.as_mutable(db.JSONB)
    )
    url: Mapped[str] = mapped_column(db.UnicodeText)
    description: Mapped[str | None] = mapped_column(db.UnicodeText)
    enabled: Mapped[bool]

    def __init__(
        self,
        event_types: set[str],
        event_filters: EventFilters,
        format: OutgoingWebhookFormat,
        url: str,
        enabled: bool,
        *,
        text_prefix: str | None = None,
        extra_fields: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> None:
        self.event_types = event_types
        self.event_filters = event_filters
        self._format = format.name
        self.text_prefix = text_prefix
        self.extra_fields = extra_fields
        self.url = url
        self.description = description
        self.enabled = enabled

    @hybrid_property
    def event_types(self) -> set[str]:
        return set(self._event_types)

    @event_types.setter
    def event_types(self, event_types: set[str]) -> None:
        self._event_types = list(event_types)

    @hybrid_property
    def format(self) -> OutgoingWebhookFormat:
        return OutgoingWebhookFormat[self._format]

    @format.setter
    def format(self, format: OutgoingWebhookFormat) -> None:
        self._format = format.name
