"""
byceps.blueprints.admin.authorization.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from ....services.authorization import authz_service
from ....services.user import user_service
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
        authz_service.get_assigned_roles_for_permissions()
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
    roles_permissions_users = (
        authz_service.get_all_roles_with_permissions_and_users()
    )

    user_ids = {
        user.id for _, _, users in roles_permissions_users for user in users
    }
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'roles_permissions_users': roles_permissions_users,
        'users_by_id': users_by_id,
    }


@blueprint.get('/roles/<role_id>')
@permission_required('role.view')
@templated
def role_view(role_id):
    """View role details."""
    role = authz_service.find_role(role_id)

    if role is None:
        abort(404)

    all_permissions = permission_registry.get_registered_permissions()

    role_permission_ids = authz_service.get_permission_ids_for_role(role.id)

    permissions = {
        permission
        for permission in all_permissions
        if permission.id in role_permission_ids
    }

    user_ids = authz_service.find_user_ids_for_role(role.id)
    users = user_service.get_users(user_ids, include_avatars=True)

    return {
        'role': role,
        'permissions': permissions,
        'users': users,
    }
