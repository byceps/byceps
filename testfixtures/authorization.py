"""
testfixtures.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authorization.models import Permission, Role


def create_permission(id, title=None):
    return Permission(id, title)


def create_role(id, title=None):
    if title is None:
        title = id

    return Role(id, title)
