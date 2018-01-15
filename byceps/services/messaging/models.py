"""
byceps.services.messaging.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import db, generate_uuid
from ...util.instances import ReprBuilder

from ..user.models.user import User


class Message(db.Model):
    """A message sent from one user to another."""
    __tablename__ = 'messages'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    sender_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    sender = db.relationship(User, foreign_keys=[sender_id])
    recipient_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    recipient = db.relationship(User, foreign_keys=[recipient_id])
    subject = db.Column(db.Unicode(40), nullable=True)
    body = db.Column(db.UnicodeText, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, sender_id, recipient_id, body, *, subject=None):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.subject = subject
        self.body = body

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('created_at') \
            .add('sender', self.sender.screen_name) \
            .add('recipient', self.recipient.screen_name) \
            .add_with_lookup('subject') \
            .add_custom('read' if self.is_read else 'unread') \
            .build()
