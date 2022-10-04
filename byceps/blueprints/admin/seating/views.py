"""
byceps.blueprints.admin.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from ....services.party import party_service
from ....services.seating import (
    area_service as seating_area_service,
    seat_group_service,
    seat_service,
)
from ....services.ticketing import (
    category_service as ticketing_category_service,
)
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to

from .forms import AreaCreateForm


blueprint = create_blueprint('seating_admin', __name__)


@blueprint.get('/<party_id>')
@permission_required('seating.view')
@templated
def index_for_party(party_id):
    """List seating areas for that party."""
    party = _get_party_or_404(party_id)

    seat_count = seat_service.count_seats_for_party(party.id)
    area_count = seating_area_service.count_areas_for_party(party.id)
    category_count = ticketing_category_service.count_categories_for_party(
        party.id
    )
    group_count = seat_group_service.count_seat_groups_for_party(party.id)

    return {
        'party': party,
        'seat_count': seat_count,
        'area_count': area_count,
        'category_count': category_count,
        'group_count': group_count,
    }


@blueprint.get('/parties/<party_id>/areas', defaults={'page': 1})
@blueprint.get('/parties/<party_id>/areas/pages/<int:page>')
@permission_required('seating.view')
@templated
def area_index(party_id, page):
    """List seating areas for that party."""
    party = _get_party_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    areas_with_utilization = (
        seating_area_service.get_areas_with_seat_utilization_paginated(
            party.id, page, per_page
        )
    )

    seat_utilizations = [awu[1] for awu in areas_with_utilization.items]
    total_seat_utilization = seat_service.aggregate_seat_utilizations(
        seat_utilizations
    )

    return {
        'party': party,
        'per_page': per_page,
        'areas_with_utilization': areas_with_utilization,
        'total_seat_utilization': total_seat_utilization,
    }


@blueprint.get('/parties/<party_id>/areas/create')
@permission_required('seating.administrate')
@templated
def area_create_form(party_id, erroneous_form=None):
    """Show form to create a seating area."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else AreaCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.post('/parties/<party_id>/areas')
@permission_required('seating.administrate')
def area_create(party_id):
    """Create a seating area."""
    party = _get_party_or_404(party_id)

    form = AreaCreateForm(request.form)
    if not form.validate():
        return area_create_form(party.id, form)

    slug = form.slug.data.strip()
    title = form.title.data.strip()

    area = seating_area_service.create_area(party.id, slug, title)

    flash_success(
        gettext('Seating area "%(title)s" has been created.', title=area.title)
    )

    return redirect_to('.area_index', party_id=party.id)


@blueprint.get('/parties/<party_id>/seat_groups')
@permission_required('seating.view')
@templated
def seat_group_index(party_id):
    """List seat groups for that party."""
    party = _get_party_or_404(party_id)

    groups = seat_group_service.get_all_seat_groups_for_party(party.id)

    return {
        'party': party,
        'groups': groups,
    }


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
