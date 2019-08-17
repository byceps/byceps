"""
byceps.services.newsletter.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ...database import db
from ...typing import UserID
from ...util.instances import ReprBuilder

from .transfer.models import ListID
from .types import SubscriptionState


class List(db.Model):
    """A newsletter list users can subscribe to."""
    __tablename__ = 'newsletter_lists'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, list_id: ListID, title: str) -> None:
        self.id = list_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class Subscription(db.Model):
    """A user's declaration on wanting/not wanting to receive
    newsletters from this list.
    """
    __tablename__ = 'newsletter_subscriptions'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    list_id = db.Column(db.UnicodeText, db.ForeignKey('newsletter_lists.id'), primary_key=True)
    expressed_at = db.Column(db.DateTime, primary_key=True)
    _state = db.Column('state', db.UnicodeText, nullable=False)

    def __init__(self, user_id: UserID, list_id: ListID,
                 expressed_at: datetime, state: SubscriptionState) -> None:
        self.user_id = user_id
        self.list_id = list_id
        self.expressed_at = expressed_at
        self.state = state

    @hybrid_property
    def state(self) -> SubscriptionState:
        return SubscriptionState[self._state]

    @state.setter
    def state(self, state: SubscriptionState) -> None:
        assert state is not None
        self._state = state.name

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('user_id') \
            .add_with_lookup('list_id') \
            .add_with_lookup('expressed_at') \
            .add('state', self.state.name) \
            .build()


Subscriber = namedtuple('Subscriber', ['screen_name', 'email_address'])
