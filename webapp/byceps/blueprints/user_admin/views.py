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


permission_registry.register_enum(UserPermission)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@permission_required(UserPermission.list)
@templated
def index(page):
    """List users."""
    per_page = 20
    users = User.query \
        .order_by(User.created_at.desc()) \
        .paginate(page, per_page)
    return {'users': users}


@blueprint.route('/<id>')
@templated
def view(id):
    """Show a user's interal profile."""
    user = User.query.get_or_404(id)
    return {'user': user}
