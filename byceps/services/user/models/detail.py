"""
byceps.services.user.models.detail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from sqlalchemy.ext.mutable import MutableDict

from ....database import db
from ....util.datetime.calc import calculate_age, calculate_days_until
from ....util.datetime.monthday import MonthDay
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
    def full_name(self) -> str:
        names = [self.first_names, self.last_name]
        return ' '.join(filter(None, names)) or None

    @property
    def age(self) -> int:
        """Return the user's current age."""
        return calculate_age(self.date_of_birth, date.today())

    @property
    def days_until_next_birthday(self) -> int:
        """Return the number of days until the user's next birthday."""
        return calculate_days_until(self.date_of_birth, date.today())

    @property
    def is_birthday_today(self) -> bool:
        """Return `True` if today is the user's birthday."""
        return MonthDay.of(self.date_of_birth).matches(date.today())

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('user_id') \
            .add_with_lookup('first_names') \
            .add_with_lookup('last_name') \
            .build()
