# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime
from operator import attrgetter

from flask import url_for
from werkzeug.routing import BuildError

from ...database import db, generate_uuid
from ...util.instances import ReprBuilder

from ..user.models import User


class ContentPage(db.Model):
    """A content page."""
    __tablename__ = 'content_pages'

    name = db.Column(db.Unicode(40), primary_key=True)
    url = db.Column(db.Unicode(40), unique=True)

    def generate_url(self):
        try:
            name = 'contentpage.{}'.format(self.name)
            return url_for(name)
        except BuildError:
            return None

    def get_latest_version(self):
        """Return the most recent version.

        A page is excepted to have at least one version (the initial
        one).
        """
        return self.get_versions()[0]

    def get_versions(self):
        """Return all versions, sorted from most recent to oldest."""
        return list(
            sorted(self.versions, key=attrgetter('created_at'), reverse=True))

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('name') \
            .add_with_lookup('url') \
            .build()


class ContentPageVersion(db.Model):
    """A snapshot of a content page at a certain time."""
    __tablename__ = 'content_page_versions'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    page_name = db.Column(db.Unicode(40), db.ForeignKey('content_pages.name'))
    page = db.relationship(ContentPage, backref='versions')
    created_at = db.Column(db.DateTime, default=datetime.now)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    creator = db.relationship(User)
    title = db.Column(db.Unicode(80))
    body = db.Column(db.UnicodeText)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('page') \
            .add_with_lookup('created_at') \
            .add_with_lookup('creator') \
            .add_with_lookup('title') \
            .add('body length', len(self.body)) \
            .build()
