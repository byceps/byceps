"""
byceps.services.consent.models.subject
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder


class Subject(db.Model):
    """A subject that requires users' consent."""
    __tablename__ = 'consent_subjects'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    name = db.Column(db.Unicode(80), unique=True, nullable=False)
    title = db.Column(db.Unicode(80), unique=True, nullable=False)

    def __init__(self, name: str, title: str) -> None:
        self.name = name
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('name') \
            .add_with_lookup('title') \
            .build()
