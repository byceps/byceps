# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import request

from ...database import db
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..shop.service import get_orders_placed_by_user
from ..user.models import User, UserDetail

from .authorization import UserPermission


blueprint = create_blueprint('user_admin', __name__)


permission_registry.register_enum(UserPermission)


@blueprint.route('/', defaults={'page': 1})
@blueprint.route('/pages/<int:page>')
@permission_required(UserPermission.list)
@templated
def index(page):
    """List users."""
    query = User.query \
        .options(db.joinedload('detail')) \
        .order_by(User.created_at.desc())

    search_term = request.args.get('search_term', default='').strip()
    if search_term:
        ilike_pattern = '%{}%'.format(search_term)
        query = query \
            .join(UserDetail) \
            .filter(
                db.or_(
                    User.screen_name.ilike(ilike_pattern),
                    UserDetail.first_names.ilike(ilike_pattern),
                    UserDetail.last_name.ilike(ilike_pattern)
                )
            )

        only = None

        per_page = 100
    else:
        only = request.args.get('only')
        if only == 'enabled':
            query = query.filter_by(enabled=True)
        elif only == 'disabled':
            query = query.filter_by(enabled=False)
        else:
            only = None

        per_page = request.args.get('per_page', type=int, default=20)

    users = query.paginate(page, per_page)

    total_enabled = User.query.filter_by(enabled=True).count()
    total_disabled = User.query.filter_by(enabled=False).count()
    total_overall = total_enabled + total_disabled

    return {
        'users': users,
        'total_enabled': total_enabled,
        'total_disabled': total_disabled,
        'total_overall': total_overall,
        'only': only,
        'search_term': search_term,
    }


@blueprint.route('/<uuid:id>')
@templated
def view(id):
    """Show a user's interal profile."""
    user = User.query.get_or_404(id)
    orders = get_orders_placed_by_user(user)
    return {
        'user': user,
        'orders': orders,
    }
