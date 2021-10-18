"""
byceps.services.authentication.api.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.mutable import MutableList

from ....database import db, generate_uuid
from ....typing import UserID

from ...authorization.transfer.models import PermissionID


class ApiToken(db.Model):
    """An authentication and authorization token for API clients."""

    __tablename__ = 'api_tokens'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.UnicodeText, nullable=False)
    permissions = db.Column(MutableList.as_mutable(db.JSONB), nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        creator_id: UserID,
        token: str,
        permissions: set[PermissionID],
        *,
        description: Optional[str],
    ) -> None:
        self.creator_id = creator_id
        self.token = token
        self.permissions = list(permissions)
        self.description = description
