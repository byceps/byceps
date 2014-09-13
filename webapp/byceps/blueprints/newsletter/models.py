# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime
from enum import Enum

from flask import g
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import db
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..user.models import User


SubscriptionState = Enum('SubscriptionState', ['requested', 'declined'])


class Subscription(db.Model):
    """A user's declaration that he/she wants or does not want to receive the
    newsletter for this brand.
    """
    __tablename__ = 'newsletter_subscriptions'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    brand = db.relationship(Brand)
    expressed_at = db.Column(db.DateTime, default=datetime.now, primary_key=True)
    _state = db.Column('state', db.Unicode(20), nullable=False)

    def __init__(self, user, state):
        self.user = user
        self.brand = g.party.brand
        self.state = state

    @hybrid_property
    def state(self):
        return SubscriptionState[self._state]

    @state.setter
    def state(self, state):
        assert state is not None
        self._state = state.name

    def __repr__(self):
        return ReprBuilder(self) \
            .add('user', self.user.screen_name) \
            .add('brand', self.brand.title) \
            .add_with_lookup('expressed_at') \
            .add('state', self.state.name) \
            .build()

    @classmethod
    def get_state_for_user(cls, user):
        """Return the user's current subscription state."""
        current_subscription = cls.query \
            .filter_by(user=user) \
            .order_by(cls.expressed_at.desc()) \
            .first()

        if current_subscription is None:
            return SubscriptionState.declined

        return current_subscription.state
