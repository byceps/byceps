# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...config import get_ticket_management_enabled
from ...util.framework import create_blueprint
from ...util.templating import templated

from . import service


blueprint = create_blueprint('seating', __name__)


@blueprint.route('/')
@templated
def index():
    """List areas."""
    areas = service.get_areas_for_party(g.party)

    return {
        'areas': areas,
    }


@blueprint.route('/areas/<slug>')
@templated
def view_area(slug):
    """View area."""
    area = service.find_area_for_party_by_slug(g.party, slug)
    if area is None:
        abort(404)

    ticket_management_enabled = get_ticket_management_enabled()

    return {
        'area': area,
        'ticket_management_enabled': ticket_management_enabled,
    }
