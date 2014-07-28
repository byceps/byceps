# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import url_for
from werkzeug.routing import BuildError

from ...database import db, generate_uuid
from ...util.instances import ReprBuilder

from ..user.models import User


class ContentPage(db.Model):
    """A content page."""
    __tablename__ = 'content_pages'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    creator = db.relationship(User)
    name = db.Column(db.Unicode(40))
    url = db.Column(db.Unicode(40))
    body = db.Column(db.UnicodeText)

    def generate_url(self):
        try:
            name = 'contentpage.{}'.format(self.name)
            return url_for(name)
        except BuildError:
            return None

    def __repr__(self):
        return ReprBuilder(self) \
            .add('id') \
            .add('created_at') \
            .add('creator') \
            .add('name') \
            .add('url') \
            .build()
