# -*- coding: utf-8 -*-

"""
byceps.services.newsletter.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ...blueprints.brand.models import Brand
from ...blueprints.user.models.user import User
from ...database import db
from ...util.instances import ReprBuilder

from .types import SubscriptionState


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

    def __init__(self, user_id, brand_id, state):
        self.user_id = user_id
        self.brand_id = brand_id
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
            .add_with_lookup('user_id') \
            .add_with_lookup('brand_id') \
            .add_with_lookup('expressed_at') \
            .add('state', self.state.name) \
            .build()
