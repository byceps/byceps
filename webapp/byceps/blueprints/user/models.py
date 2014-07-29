# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime
from itertools import chain
from operator import attrgetter
from pathlib import Path
from uuid import UUID

from flask import current_app
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, \
    generate_password_hash as _generate_password_hash

from ...database import db, generate_uuid
from ...util.image import ImageType
from ...util.instances import ReprBuilder


PASSWORD_HASH_METHOD = 'pbkdf2:sha1'

GUEST_USER_ID = UUID('00000000-0000-0000-0000-000000000000')


class AnonymousUser(object):

    id = GUEST_USER_ID
    is_enabled = False

    def is_anonymous(self):
        return True

    def is_active(self):
        return False

    @property
    def roles(self):
        return frozenset()

    @property
    def permissions(self):
        return frozenset()

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class User(db.Model):
    """A user."""
    __tablename__ = 'users'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    screen_name = db.Column(db.Unicode(40), unique=True)
    email_address = db.Column(db.Unicode(80), unique=True)
    password_hash = db.Column(db.Unicode(66))
    is_enabled = db.Column(db.Boolean, default=False)
    avatar_image_created_at = db.Column(db.DateTime)
    _avatar_image_type = db.Column(db.Unicode(4))

    roles = association_proxy('user_roles', 'role')

    @classmethod
    def create(cls, screen_name, email_address, password):
        user = cls(
            screen_name=normalize_name(screen_name),
            email_address=normalize_email_address(email_address),
            password_hash=generate_password_hash(password))

        detail = UserDetail(user=user)

        return user

    @classmethod
    def authenticate(cls, screen_name, password):
        """Try to authenticate the user.

        Return the associated user object on success, or `None` on
        failure.
        """
        user = cls.query.filter_by(screen_name=screen_name).first()

        if user is None:
            # User name is unknown.
            return

        if not check_password_hash(user.password_hash, password):
            # Password does not match.
            return

        if not user.is_active():
            # User account is disabled.
            return

        return user

    @classmethod
    def load(cls, id):
        """Load user with the given ID."""
        if id is None:
            return AnonymousUser()

        user = cls.query.get(id)
        if (user is None) or not user.is_enabled:
            return AnonymousUser()

        return user

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.is_enabled

    @property
    def permissions(self):
        models = frozenset(
            chain.from_iterable(role.permissions for role in self.roles))
        return frozenset(map(attrgetter('enum_member'), models))

    @property
    def has_avatar_image(self):
        return None not in {
            self.avatar_image_created_at,
            self.avatar_image_type,
        }

    def set_avatar_image(self, created_at, image_type):
        self.avatar_image_created_at = created_at
        self.avatar_image_type = image_type

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
        timestamp = self.avatar_image_created_at.strftime('%s')
        name_without_suffix = '{}_{}'.format(self.id, timestamp)
        suffix = '.' + self.avatar_image_type.name
        return Path(name_without_suffix).with_suffix(suffix)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('screen_name') \
            .add_with_lookup('email_address') \
            .add_with_lookup('is_enabled') \
            .add_with_lookup('has_avatar_image') \
            .build()


class UserDetail(db.Model):
    """Detailed information about a specific user."""
    __tablename__ = 'user_details'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('detail', uselist=False))
    first_names = db.Column(db.Unicode(40))
    last_name = db.Column(db.Unicode(40))
    full_name = db.column_property(
        (first_names + ' ' + last_name).label('full_name'))

    def __repr__(self):
        return ReprBuilder(self) \
            .add('user_id') \
            .add('first_names') \
            .add('last_name') \
            .build()


def normalize_name(screen_name):
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
