# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprin
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import RolePermission


blueprint = create_blueprint('authorization_admin', __name__)


permission_registry.register_enum(RolePermission)


@blueprint.route('/permissions')
@permission_required(RolePermission.list)
@templated
def permission_index():
    """List permissions."""
    permissions = get_permissions_with_titles()

    return {'permissions': permissions}


@blueprint.route('/roles')
@permission_required(RolePermission.list)
@templated
def role_index():
    """List roles."""
    roles = get_roles_with_titles()

    return {'roles': roles}
