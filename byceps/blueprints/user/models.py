# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime
from collections import namedtuple
from itertools import chain
from operator import attrgetter
from pathlib import Path
from uuid import UUID

from flask import current_app
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, \
    generate_password_hash as _generate_password_hash

from ...config import get_site_mode
from ...database import db, generate_uuid
from ...util.datetime import calculate_age, calculate_days_until, MonthDay
from ...util.image import ImageType
from ...util.instances import ReprBuilder


PASSWORD_HASH_METHOD = 'pbkdf2:sha1'

GUEST_USER_ID = UUID('00000000-0000-0000-0000-000000000000')


class AnonymousUser(object):

    id = GUEST_USER_ID
    enabled = False

    @property
    def is_anonymous(self):
        return True

    @property
    def is_active(self):
        return False

    @property
    def roles(self):
        return frozenset()

    @property
    def permissions(self):
        return frozenset()

    def has_permission(self, permission):
        return False

    def has_any_permission(self, *permissions):
        return False

    @property
    def has_avatar_image(self):
        return False

    @property
    def is_orga_for_any_brand(self):
        return False

    def is_orga_for_party(self, party):
        return False

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class User(db.Model):
    """A user."""
    __tablename__ = 'users'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    screen_name = db.Column(db.Unicode(40), unique=True, nullable=False)
    email_address = db.Column(db.Unicode(80), unique=True, nullable=False)
    password_hash = db.Column(db.Unicode(66))
    auth_token = db.Column(db.Uuid)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    avatar_image_created_at = db.Column(db.DateTime)
    _avatar_image_type = db.Column(db.Unicode(4))
    legacy_id = db.Column(db.Integer)

    roles = association_proxy('user_roles', 'role')

    @classmethod
    def create(cls, screen_name, email_address, password):
        user = cls()
        user.set_screen_name(screen_name)
        user.set_email_address(email_address)
        user.set_password(password)
        user.set_new_auth_token()

        detail = UserDetail(user=user)

        return user

    def set_screen_name(self, screen_name):
        self.screen_name = normalize_screen_name(screen_name)

    def set_email_address(self, email_address):
        self.email_address = normalize_email_address(email_address)

    def set_password(self, password):
        """Calculate and store a hash value for the password."""
        self.password_hash = generate_password_hash(password)

    def is_password_valid(self, password):
        """Return `True` if the password is valid for this user, and
        `False` otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def set_new_auth_token(self):
        """Generate and store a new authentication token."""
        self.auth_token = generate_uuid()

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.enabled

    @property
    def permissions(self):
        models = frozenset(
            chain.from_iterable(role.permissions for role in self.roles))
        return frozenset(map(attrgetter('enum_member'), models))

    def has_permission(self, permission):
        return permission in self.permissions

    def has_any_permission(self, *permissions):
        return any(map(self.has_permission, permissions))

    @property
    def has_avatar_image(self):
        return None not in {
            self.avatar_image_created_at,
            self.avatar_image_type,
        }

    def set_avatar_image(self, created_at, image_type):
        self.avatar_image_created_at = created_at
        self.avatar_image_type = image_type

    def remove_avatar_image(self):
        self.avatar_image_created_at = None
        self.avatar_image_type = None

    @hybrid_property
    def avatar_image_type(self):
        type_str = self._avatar_image_type
        if type_str is not None:
            return ImageType[type_str]

    @avatar_image_type.setter
    def avatar_image_type(self, type_):
        self._avatar_image_type = type_.name if type_ is not None else None

    @property
    def avatar_image_path(self):
        if not self.has_avatar_image:
            return None

        path = current_app.config['PATH_USER_AVATAR_IMAGES']
        filename = self.avatar_image_filename
        return path / filename

    @property
    def avatar_image_filename(self):
        timestamp = int(self.avatar_image_created_at.timestamp())
        name_without_suffix = '{}_{:d}'.format(self.id, timestamp)
        suffix = '.' + self.avatar_image_type.name
        return Path(name_without_suffix).with_suffix(suffix)

    @property
    def is_orga_for_any_brand(self):
        return bool(self.orga_flags)

    def is_orga_for_party(self, party):
        if get_site_mode().is_admin():
            # Current party is not defined in admin mode.
            return False

        parties = {ms.orga_team.party for ms in self.orga_team_memberships}
        return party in parties

    def __eq__(self, other):
        return (other is not None) and (self.id == other.id)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('screen_name') \
            .build()


class UserDetail(db.Model):
    """Detailed information about a specific user."""
    __tablename__ = 'user_details'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('detail', uselist=False))
    first_names = db.Column(db.Unicode(40))
    last_name = db.Column(db.Unicode(40))
    date_of_birth = db.Column(db.Date)
    country = db.Column(db.Unicode(60))
    zip_code = db.Column(db.Unicode(5))
    city = db.Column(db.Unicode(40))
    street = db.Column(db.Unicode(40))
    phone_number = db.Column(db.Unicode(20))
    internal_comment = db.Column(db.Unicode(200))

    @property
    def full_name(self):
        names = [self.first_names, self.last_name]
        return ' '.join(filter(None, names)) or None

    @property
    def age(self):
        """Return the user's current age."""
        return calculate_age(self.date_of_birth, date.today())

    @property
    def days_until_next_birthday(self):
        """Return the number of days until the user's next birthday."""
        return calculate_days_until(self.date_of_birth, date.today())

    @property
    def is_birthday_today(self):
        """Return `True` if today is the user's birthday."""
        return MonthDay.of(self.date_of_birth).matches(date.today())

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('user_id') \
            .add_with_lookup('first_names') \
            .add_with_lookup('last_name') \
            .build()


Country = namedtuple('Country', 'name alpha2 alpha3')


def normalize_screen_name(screen_name):
    """Normalize the screen name, or raise an exception if invalid."""
    normalized = screen_name.strip()
    if not normalized or (' ' in normalized) or ('@' in normalized):
        raise ValueError('Invalid screen name: \'{}\''.format(screen_name))
    return normalized


def normalize_email_address(email_address):
    """Normalize the e-mail address, or raise an exception if invalid."""
    normalized = email_address.strip()
    if not normalized or (' ' in normalized) or ('@' not in normalized):
        raise ValueError('Invalid email address: \'{}\''.format(email_address))
    return normalized


def generate_password_hash(password):
    """Generate a salted hash for the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)
