"""
byceps.blueprints.admin.authorization.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from ....services.authorization import service as authorization_service
from ....services.user import service as user_service
from ....util.authorization import permission_registry
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required


blueprint = create_blueprint('authorization_admin', __name__)


@blueprint.get('/permissions')
@permission_required('role.view')
@templated
def permission_index():
    """List permissions."""
    all_permissions = permission_registry.get_registered_permissions()

    role_ids_by_permission_id = (
        authorization_service.get_assigned_roles_for_permissions()
    )

    permissions_and_roles = [
        (permission, role_ids_by_permission_id.get(permission.id, frozenset()))
        for permission in all_permissions
    ]

    return {'permissions_and_roles': permissions_and_roles}


@blueprint.get('/roles')
@permission_required('role.view')
@templated
def role_index():
    """List roles."""
    roles = authorization_service.get_all_roles_with_titles()

    user_ids = {user.id for role in roles for user in role.users}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'roles': roles,
        'users_by_id': users_by_id,
    }


@blueprint.get('/roles/<role_id>')
@permission_required('role.view')
@templated
def role_view(role_id):
    """View role details."""
    role = authorization_service.find_role(role_id)

    if role is None:
        abort(404)

    all_permissions = permission_registry.get_registered_permissions()

    role_permission_ids = authorization_service.get_permission_ids_for_role(
        role.id
    )

    permissions = {
        permission
        for permission in all_permissions
        if permission.id in role_permission_ids
    }

    user_ids = authorization_service.find_user_ids_for_role(role.id)
    users = user_service.get_users(user_ids, include_avatars=True)

    return {
        'role': role,
        'permissions': permissions,
        'users': users,
    }
