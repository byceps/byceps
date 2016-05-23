# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.models.badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from .user import User


class Badge(db.Model):
    """A global badge that can be awarded to a user."""
    __tablename__ = 'user_badges'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    label = db.Column(db.Unicode(80), unique=True, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    image_filename = db.Column(db.Unicode(80), nullable=False)

    recipients = association_proxy('awardings', 'user',
        creator=lambda user: BadgeAwarding(None, user.id))

    @property
    def image_url(self):
        filename = 'users/badges/{}'.format(self.image_filename)
        return url_for('global_file', filename=filename)

    def __init__(self, label, image_filename, *, description=None):
        self.label = label
        self.description = description
        self.image_filename = image_filename

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('label') \
            .build()


class BadgeAwarding(db.Model):
    """The awarding of a badge to a user."""
    __tablename__ = 'user_badge_awardings'

    badge_id = db.Column(db.Uuid, db.ForeignKey('user_badges.id'), primary_key=True)
    badge = db.relationship(Badge, collection_class=set,
                            backref=db.backref('awardings', collection_class=set))
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, collection_class=set,
                            backref=db.backref('badge_awardings', collection_class=set))
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, badge_id, user_id):
        self.badge_id = badge_id
        self.user_id = user_id
