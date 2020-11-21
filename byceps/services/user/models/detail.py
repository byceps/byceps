"""
byceps.services.user.models.detail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy.ext.mutable import MutableDict

from ....database import db
from ....util.instances import ReprBuilder


class UserDetail(db.Model):
    """Detailed information about a specific user."""

    __tablename__ = 'user_details'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('detail', uselist=False))
    first_names = db.Column(db.UnicodeText)
    last_name = db.Column(db.UnicodeText)
    date_of_birth = db.Column(db.Date)
    country = db.Column(db.UnicodeText)
    zip_code = db.Column(db.UnicodeText)
    city = db.Column(db.UnicodeText)
    street = db.Column(db.UnicodeText)
    phone_number = db.Column(db.UnicodeText)
    internal_comment = db.Column(db.UnicodeText)
    extras = db.Column(MutableDict.as_mutable(db.JSONB))

    @property
    def full_name(self) -> Optional[str]:
        names = [self.first_names, self.last_name]
        return ' '.join(filter(None, names)) or None

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('user_id') \
            .add_with_lookup('first_names') \
            .add_with_lookup('last_name') \
            .build()
