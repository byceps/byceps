"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from flask import appcontext_pushed, g

from byceps.application import create_app
from byceps.services.authorization import service as authorization_service

from .base import CONFIG_FILENAME_TEST_PARTY


@contextmanager
def app_context(*, config_filename=CONFIG_FILENAME_TEST_PARTY):
    app = create_app(config_filename)

    with app.app_context():
        yield app


@contextmanager
def current_party_set(app, party):
    def handler(sender, **kwargs):
        g.party = party

    with appcontext_pushed.connected_to(handler, app):
        yield


@contextmanager
def current_user_set(app, user):
    def handler(sender, **kwargs):
        g.current_user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


def assign_permissions_to_user(user_id, role_id, permission_ids):
    """Create the role and permissions, assign the permissions to the
    role, and assign the role to the user.
    """
    role = authorization_service.create_role(role_id, role_id)

    for permission_id in permission_ids:
        permission = authorization_service.create_permission(permission_id,
                                                             permission_id)
        authorization_service.assign_permission_to_role(permission.id, role.id)

    authorization_service.assign_role_to_user(user_id, role.id)
