# -*- coding: utf-8 -*-

"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from flask import appcontext_pushed, g

from byceps.services.authorization import service as authorization_service


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


def assign_permissions_to_user(user, role_id, permission_ids):
    """Create the role and permissions, assign the permissions to the
    role, and assign the role to the user.
    """
    role = authorization_service.create_role(role_id, role_id)

    for permission_id in permission_ids:
        permission = authorization_service.create_permission(permission_id,
                                                             permission_id)
        authorization_service.assign_permission_to_role(permission, role)

    authorization_service.assign_role_to_user(role, user)
