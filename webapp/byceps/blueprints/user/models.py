# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime
from itertools import chain
from operator import attrgetter
from uuid import UUID

from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import check_password_hash, \
    generate_password_hash as _generate_password_hash

from ...database import db, generate_uuid
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
    name = db.Column(db.Unicode(40), unique=True)
    email_address = db.Column(db.Unicode(80), unique=True)
    password_hash = db.Column(db.Unicode(66))
    is_enabled = db.Column(db.Boolean, default=False)

    roles = association_proxy('user_roles', 'role')

    @classmethod
    def create(cls, name, email_address, password):
        user = cls(
            name=normalize_name(name),
            email_address=normalize_email_address(email_address),
            password_hash=generate_password_hash(password))

        detail = UserDetail(user=user)

        return user

    @classmethod
    def authenticate(cls, name, password):
        """Try to authenticate the user.

        Return the associated user object on success, or `None` on
        failure.
        """
        user = cls.query.filter_by(name=name).first()

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

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('name') \
            .add_with_lookup('email_address') \
            .add_with_lookup('is_enabled') \
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


def normalize_name(name):
    """Normalize the user name, or raise an exception if invalid."""
    normalized = name.strip()
    if not normalized or (' ' in normalized) or ('@' in normalized):
        raise ValueError('Invalid user name: \'{}\''.format(name))
    return normalized


def normalize_email_address(email_address):
    """Normalize the e-mail address, or raise an exception if invalid."""
    normalized = email_address.strip()
    if not normalized or (' ' in normalized) or ('@' not in normalized):
        raise ValueError('Invalid e-mail address: \'{}\''.format(email_address))
    return normalized


def generate_password_hash(password):
    """Generate a salted hash for the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)
