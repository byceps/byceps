"""
byceps.blueprints.admin.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from ....services.party import party_service
from ....services.seating.models import SeatingArea, SeatingAreaID
from ....services.seating import (
    seat_group_service,
    seat_service,
    seating_area_service,
    seating_area_tickets_service,
)
from ....services.ticketing import ticket_category_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to

from .forms import AreaCreateForm, AreaUpdateForm


blueprint = create_blueprint('seating_admin', __name__)


@blueprint.get('/<party_id>')
@permission_required('seating.view')
@templated
def index_for_party(party_id):
    """List seating areas for that party."""
    party = _get_party_or_404(party_id)

    seat_count = seat_service.count_seats_for_party(party.id)
    area_count = seating_area_service.count_areas_for_party(party.id)
    category_count = ticket_category_service.count_categories_for_party(
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


@blueprint.get('/parties/<party_id>/areas')
@permission_required('seating.view')
@templated
def area_index(party_id):
    """List seating areas for that party."""
    party = _get_party_or_404(party_id)

    areas_with_utilization = (
        seating_area_service.get_areas_with_seat_utilization(party.id)
    )

    seat_utilizations = [awu[1] for awu in areas_with_utilization]
    total_seat_utilization = seat_service.aggregate_seat_utilizations(
        seat_utilizations
    )

    return {
        'party': party,
        'areas_with_utilization': areas_with_utilization,
        'total_seat_utilization': total_seat_utilization,
    }


@blueprint.get('/areas/<area_id>')
@permission_required('seating.view')
@templated
def area_view(area_id):
    """Show seating area."""
    area = _get_area_or_404(area_id)

    party = party_service.get_party(area.party_id)

    seats_with_tickets = seat_service.get_seats_with_tickets_for_area(area.id)

    users_by_id = seating_area_tickets_service.get_users(seats_with_tickets, [])

    seats_and_tickets = seating_area_tickets_service.get_seats_and_tickets(
        seats_with_tickets, users_by_id
    )

    return {
        'party': party,
        'area': area,
        'seats_and_tickets': seats_and_tickets,
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
    image_filename = form.image_filename.data.strip()
    image_width = form.image_width.data
    image_height = form.image_height.data

    area = seating_area_service.create_area(
        party.id,
        slug,
        title,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
    )

    flash_success(
        gettext('Seating area "%(title)s" has been created.', title=area.title)
    )

    return redirect_to('.area_index', party_id=party.id)


@blueprint.get('/areas/<area_id>/update')
@permission_required('seating.administrate')
@templated
def area_update_form(area_id, erroneous_form=None):
    """Show form to update a seating area."""
    area = _get_area_or_404(area_id)

    party = party_service.get_party(area.party_id)

    form = erroneous_form if erroneous_form else AreaUpdateForm(obj=area)

    return {
        'party': party,
        'area': area,
        'form': form,
    }


@blueprint.post('/areas/<area_id>')
@permission_required('seating.administrate')
def area_update(area_id):
    """Update a seating area."""
    area = _get_area_or_404(area_id)

    form = AreaUpdateForm(request.form)
    if not form.validate():
        return area_update_form(area.id, form)

    slug = form.slug.data.strip()
    title = form.title.data.strip()
    image_filename = form.image_filename.data.strip()
    image_width = form.image_width.data
    image_height = form.image_height.data

    area = seating_area_service.update_area(
        area.id,
        slug,
        title,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
    )

    flash_success(
        gettext('Seating area "%(title)s" has been updated.', title=area.title)
    )

    return redirect_to('.area_view', area_id=area.id)


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


def _get_area_or_404(area_id: SeatingAreaID) -> SeatingArea:
    area = seating_area_service.find_area(area_id)

    if area is None:
        abort(404)

    return area
