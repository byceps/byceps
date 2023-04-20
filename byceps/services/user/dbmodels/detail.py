"""
byceps.services.user.dbmodels.detail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy.ext.mutable import MutableDict

from byceps.database import db
from byceps.util.instances import ReprBuilder


class DbUserDetail(db.Model):
    """Detailed information about a specific user."""

    __tablename__ = 'user_details'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(
        'DbUser', backref=db.backref('detail', uselist=False)
    )
    first_name = db.Column(db.UnicodeText, nullable=True)
    last_name = db.Column(db.UnicodeText, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    country = db.Column(db.UnicodeText, nullable=True)
    zip_code = db.Column(db.UnicodeText, nullable=True)
    city = db.Column(db.UnicodeText, nullable=True)
    street = db.Column(db.UnicodeText, nullable=True)
    phone_number = db.Column(db.UnicodeText, nullable=True)
    internal_comment = db.Column(db.UnicodeText, nullable=True)
    extras = db.Column(MutableDict.as_mutable(db.JSONB), nullable=True)

    @property
    def full_name(self) -> Optional[str]:
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)) or None

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('user_id')
            .add_with_lookup('first_name')
            .add_with_lookup('last_name')
            .build()
        )
