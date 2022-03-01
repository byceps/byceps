"""
byceps.services.consent.dbmodels.subject
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder


class Subject(db.Model):
    """A subject that requires users' consent."""

    __tablename__ = 'consent_subjects'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True, nullable=False)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    checkbox_label = db.Column(db.UnicodeText, nullable=False)
    checkbox_link_target = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        name: str,
        title: str,
        checkbox_label: str,
        checkbox_link_target: Optional[str],
    ) -> None:
        self.name = name
        self.title = title
        self.checkbox_label = checkbox_label
        self.checkbox_link_target = checkbox_link_target

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('name') \
            .add_with_lookup('title') \
            .build()
