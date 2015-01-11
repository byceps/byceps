# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...config import get_ticket_management_enabled
from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import Area


blueprint = create_blueprint('seating', __name__)


@blueprint.route('/')
@templated
def index():
    """List areas."""
    areas = Area.query.for_current_party().all()
    return {'areas': areas}


@blueprint.route('/areas/<slug>')
@templated
def view_area(slug):
    """View area."""
    area = Area.query.for_current_party().filter_by(slug=slug).first_or_404()
    ticket_management_enabled = get_ticket_management_enabled()

    return {
        'area': area,
        'ticket_management_enabled': ticket_management_enabled,
    }
