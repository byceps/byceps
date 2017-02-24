"""
byceps.blueprints.authorization_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...services.authorization import service as authorization_service
from ...util.framework.blueprint import create_blueprint
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
    permissions = authorization_service.get_all_permissions_with_titles()

    return {'permissions': permissions}


@blueprint.route('/roles')
@permission_required(RolePermission.list)
@templated
def role_index():
    """List roles."""
    roles = authorization_service.get_all_roles_with_titles()

    return {'roles': roles}
