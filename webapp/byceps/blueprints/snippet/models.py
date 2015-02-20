# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snippets of database-stored content. Can contain HTML and template
engine syntax. Can be embedded in other templates or mounted as full
page.

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import g, url_for
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.routing import BuildError

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..party.models import Party
from ..user.models import User


class BelongsToPartyQuery(BaseQuery):

    def for_current_party(self):
        return self.for_party(g.party)

    def for_party(self, party):
        return self.for_party_with_id(party.id)

    def for_party_with_id(self, party_id):
        return self.filter_by(party_id=party_id)


class Snippet(db.Model):
    """A snippet."""
    __tablename__ = 'snippets'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'name'),
    )
    query_class = BelongsToPartyQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    name = db.Column(db.Unicode(40), index=True, nullable=False)
    current_version = association_proxy('current_version_association', 'version')

    def get_latest_version(self):
        """Return the most recent version.

        A snippet is expected to have at least one version (the initial
        one).
        """
        return SnippetVersion.query.for_snippet(self).latest_first().first()

    def get_versions(self):
        """Return all versions, sorted from most recent to oldest."""
        return SnippetVersion.query.for_snippet(self).latest_first().all()

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('name') \
            .build()


class SnippetVersionQuery(BelongsToPartyQuery):

    def for_snippet(self, snippet):
        return self.filter_by(snippet=snippet)

    def latest_first(self):
        return self.order_by(SnippetVersion.created_at.desc())


class SnippetVersion(db.Model):
    """A snapshot of a snippet at a certain time."""
    __tablename__ = 'snippet_versions'
    query_class = SnippetVersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User)
    title = db.Column(db.Unicode(80))
    body = db.Column(db.UnicodeText, nullable=False)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('snippet') \
            .add_with_lookup('created_at') \
            .add_with_lookup('creator') \
            .add_with_lookup('title') \
            .add('body length', len(self.body)) \
            .build()


class CurrentVersionAssociation(db.Model):
    __tablename__ = 'snippet_current_versions'

    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), primary_key=True)
    snippet = db.relationship(Snippet, backref=db.backref('current_version_association', uselist=False))
    version_id = db.Column(db.Uuid, db.ForeignKey('snippet_versions.id'), unique=True, nullable=False)
    version = db.relationship(SnippetVersion)


class MountpointQuery(BelongsToPartyQuery):

    def for_party_with_id(self, party_id):
        return self.join(Snippet).filter_by(party_id=party_id)


class Mountpoint(db.Model):
    """The exposition of a snippet at a certain URL path."""
    __tablename__ = 'snippet_mountpoints'
    __table_args__ = (
        db.UniqueConstraint('snippet_id', 'endpoint_suffix'),
        db.UniqueConstraint('snippet_id', 'url_path'),
    )
    query_class = MountpointQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    endpoint_suffix = db.Column(db.Unicode(40), nullable=False)
    url_path = db.Column(db.Unicode(40), nullable=False)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)

    def generate_url(self):
        try:
            return url_for('snippet.{}'.format(self.endpoint_suffix))
        except BuildError:
            return None

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('endpoint_suffix') \
            .add_with_lookup('url_path') \
            .add_with_lookup('snippet') \
            .build()
