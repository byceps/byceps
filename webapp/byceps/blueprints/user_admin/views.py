# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..user.models import User

from .authorization import UserPermission


blueprint = create_blueprint('user_admin', __name__)


permission_registry.register_enum('user', UserPermission)


@blueprint.route('/')
@permission_required(UserPermission.list)
@templated
def index():
    """List users."""
    users = User.query.all()
    return {'users': users}
