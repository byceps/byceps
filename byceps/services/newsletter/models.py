"""
byceps.services.newsletter.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ...database import db
from ...typing import BrandID, UserID
from ...util.instances import ReprBuilder

from .types import SubscriptionState


class Subscription(db.Model):
    """A user's declaration that he/she wants or does not want to receive the
    newsletter for this brand.
    """
    __tablename__ = 'newsletter_subscriptions'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    expressed_at = db.Column(db.DateTime, default=datetime.now, primary_key=True)
    _state = db.Column('state', db.Unicode(20), nullable=False)

    def __init__(self, user_id: UserID, brand_id: BrandID,
                 state: SubscriptionState) -> None:
        self.user_id = user_id
        self.brand_id = brand_id
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
            .add_with_lookup('brand_id') \
            .add_with_lookup('expressed_at') \
            .add('state', self.state.name) \
            .build()


Subscriber = namedtuple('Subscriber', ['screen_name', 'email_address'])
