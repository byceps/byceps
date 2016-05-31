# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import Badge


blueprint = create_blueprint('user_badge', __name__)


@blueprint.route('/<uuid:id>')
@templated
def view(id):
    """Show information about a badge."""
    badge = Badge.query.get_or_404(id)

    return {
        'badge': badge,
    }
