# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...database import db
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..authorization.models import Permission, Role, RolePermission

from .authorization import RolePermission


blueprint = create_blueprint('authorization_admin', __name__)


permission_registry.register_enum(RolePermission)


@blueprint.route('/permissions')
@permission_required(RolePermission.list)
@templated
def permission_index():
    """List permissions."""
    permissions = Permission.query \
        .options(
            db.joinedload('role_permissions')
        ) \
        .all()
    return {'permissions': permissions}


@blueprint.route('/roles')
@permission_required(RolePermission.list)
@templated
def role_index():
    """List roles."""
    roles = Role.query \
        .options(
            db.joinedload_all('user_roles.user')
        ) \
        .all()
    return {'roles': roles}
