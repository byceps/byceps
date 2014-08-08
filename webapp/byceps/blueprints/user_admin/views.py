# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..user.models import User


blueprint = create_blueprint('user_admin', __name__)


@blueprint.route('/')
@templated
def index():
    """List users."""
    users = User.query.all()
    return {'users': users}
