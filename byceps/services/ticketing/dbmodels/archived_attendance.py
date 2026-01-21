"""
byceps.services.ticketing.dbmodels.archived_attendance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID


class DbArchivedAttendance(db.Model):
    """A user's attendance of a party.

    This is a link between a party and a user that attended it.

    While such a link is usually established through a ticket for a
    party that is assigned to a user, this entity was introduced for
    legacy data for which no information on tickets, orders, seating
    areas and so on exists anymore (or should not be migrated).

    The data for this entity is expected to be inserted from the
    outside. BYCEPS itself currently does not write any archived
    attendances (but incorporates them to be displayed on user
    profiles).
    """

    __tablename__ = 'user_archived_party_attendances'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), primary_key=True
    )
    created_at: Mapped[datetime]

    def __init__(
        self, user_id: UserID, party_id: PartyID, created_at: datetime
    ) -> None:
        self.user_id = user_id
        self.party_id = party_id
        self.created_at = created_at
