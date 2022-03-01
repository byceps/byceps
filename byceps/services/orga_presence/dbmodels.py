"""
byceps.services.orga_presence.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db, generate_uuid
from ..user.dbmodels.user import User


class TimeSlot(db.Model):
    """A time slot at a party."""

    __tablename__ = 'orga_time_slots'
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'time_slot',
    }

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False)
    type = db.Column(db.UnicodeText, index=True, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)


class Presence(TimeSlot):
    """The scheduled presence of an organizer at a party."""

    __mapper_args__ = {
        'polymorphic_identity': 'orga_presence',
    }

    orga_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    orga = db.relationship(User)


class Task(TimeSlot):
    """A scheduled task connected to a party."""

    __mapper_args__ = {
        'polymorphic_identity': 'task',
    }

    title = db.Column(db.UnicodeText)
