"""
byceps.services.orga_presence.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import UserID
from byceps.util.uuid import generate_uuid7


class DbTimeSlot(db.Model):
    """A time slot at a party."""

    __tablename__ = 'orga_time_slots'
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'time_slot',
    }

    id: Mapped[UUID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    type: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    starts_at: Mapped[datetime]
    ends_at: Mapped[datetime]


class DbPresence(DbTimeSlot):
    """The scheduled presence of an organizer at a party."""

    __mapper_args__ = {
        'polymorphic_identity': 'orga_presence',
    }

    orga_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), nullable=True
    )
    orga: Mapped[DbUser] = relationship(DbUser)


class DbTask(DbTimeSlot):
    """A scheduled task connected to a party."""

    __mapper_args__ = {
        'polymorphic_identity': 'task',
    }

    title: Mapped[str] = mapped_column(db.UnicodeText, nullable=True)
