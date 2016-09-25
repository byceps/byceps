# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ...services.seating import service as seating_service
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party import service as party_service

from .authorization import SeatingPermission


blueprint = create_blueprint('seating_admin', __name__)


permission_registry.register_enum(SeatingPermission)


@blueprint.route('/<party_id>', defaults={'page': 1})
@blueprint.route('/<party_id>/pages/<int:page>')
@permission_required(SeatingPermission.view)
@templated
def index_for_party(party_id, page):
    """List seating areas for that party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    per_page = request.args.get('per_page', type=int, default=15)
    areas = seating_service.get_areas_for_party_paginated(party, page, per_page)

    seat_total_per_area = seating_service.get_seat_total_per_area(party)

    categories = seating_service.get_categories_for_party(party)

    return {
        'party': party,
        'areas': areas,
        'seat_total_per_area': seat_total_per_area,
        'categories': categories,
    }
