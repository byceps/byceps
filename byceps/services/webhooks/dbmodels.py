"""
byceps.services.webhooks.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict, MutableList

from ...database import db, generate_uuid

from .transfer.models import EventFilters


class DbOutgoingWebhook(db.Model):
    """An outgoing webhook configuration."""

    __tablename__ = 'outgoing_webhooks'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    _event_types = db.Column(
        'event_types', MutableList.as_mutable(db.JSONB), nullable=False
    )
    event_filters = db.Column(MutableDict.as_mutable(db.JSONB), nullable=True)
    format = db.Column(db.UnicodeText, nullable=False)
    text_prefix = db.Column(db.UnicodeText, nullable=True)
    extra_fields = db.Column(MutableDict.as_mutable(db.JSONB), nullable=True)
    url = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    enabled = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        event_types: set[str],
        event_filters: EventFilters,
        format: str,
        url: str,
        enabled: bool,
        *,
        text_prefix: Optional[str] = None,
        extra_fields: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> None:
        self.event_types = event_types
        self.event_filters = event_filters
        self.format = format
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
