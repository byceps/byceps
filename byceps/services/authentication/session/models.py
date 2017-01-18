# -*- coding: utf-8 -*-

"""
byceps.services.authentication.session.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db


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
