"""
byceps.services.snippet.models.mountpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType, Optional
from uuid import UUID

from flask import url_for
from werkzeug.routing import BuildError

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from .snippet import Snippet


MountpointID = NewType('MountpointID', UUID)


class Mountpoint(db.Model):
    """The exposition of a snippet at a certain URL path."""
    __tablename__ = 'snippet_mountpoints'
    __table_args__ = (
        db.UniqueConstraint('snippet_id', 'endpoint_suffix'),
        db.UniqueConstraint('snippet_id', 'url_path'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    endpoint_suffix = db.Column(db.Unicode(40), nullable=False)
    url_path = db.Column(db.Unicode(40), nullable=False)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)

    def __init__(self, endpoint_suffix: str, url_path: str, snippet: Snippet
                ) -> None:
        self.endpoint_suffix = endpoint_suffix
        self.url_path = url_path
        self.snippet = snippet

    def generate_url(self) -> Optional[str]:
        try:
            return url_for('snippet.{}'.format(self.endpoint_suffix))
        except BuildError:
            return None

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('endpoint_suffix') \
            .add_with_lookup('url_path') \
            .add_with_lookup('snippet') \
            .build()
