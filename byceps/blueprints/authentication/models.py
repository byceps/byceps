# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db


class Credential(db.Model):
    """A user's login credential."""
    __tablename__ = 'authn_credentials'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    password_hash = db.Column(db.Unicode(80), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, password_hash, updated_at):
        self.user_id = user_id
        self.password_hash = password_hash
        self.updated_at = updated_at


class SessionToken(db.Model):
    """A user's session token."""
    __tablename__ = 'authn_session_tokens'

    token = db.Column(db.Uuid, primary_key=True)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, user_id, created_at):
        self.token = token
        self.user_id = user_id
        self.created_at = created_at
