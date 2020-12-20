"""
byceps.blueprints.admin.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask import abort, request

from ....services.brand import service as brand_service
from ....services.party import (
    service as party_service,
    settings_service as party_settings_service,
)
from ....services.ticketing import ticket_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.iterables import partition
from ....util.templatefilters import local_tz_to_utc, utc_to_local_tz
from ....util.views import redirect_to

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

from .authorization import PartyPermission
from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('party_admin', __name__)


permission_registry.register_enum(PartyPermission)


@blueprint.route('/')
@permission_required(PartyPermission.view)
@templated
def index():
    """List parties."""
    parties = party_service.get_all_parties_with_brands()
    parties.sort(key=lambda party: party.starts_at, reverse=True)

    active_parties, archived_parties = partition(
        parties, lambda party: not party.archived
    )

    brands = brand_service.get_all_brands()
    brands.sort(key=lambda brand: brand.title)

    days_by_party_id = {
        party.id: party_service.get_party_days(party) for party in parties
    }

    ticket_sale_stats_by_party_id = {
        party.id: ticket_service.get_ticket_sale_stats(party.id)
        for party in parties
    }

    return {
        'parties': parties,
        'active_parties': active_parties,
        'archived_parties': archived_parties,
        'brands': brands,
        'days_by_party_id': days_by_party_id,
        'ticket_sale_stats_by_party_id': ticket_sale_stats_by_party_id,
    }


@blueprint.route('/brands/<brand_id>', defaults={'page': 1})
@blueprint.route('/brands/<brand_id>/pages/<int:page>')
@permission_required(PartyPermission.view)
@templated
def index_for_brand(brand_id, page):
    """List parties for this brand."""
    brand = _get_brand_or_404(brand_id)

    per_page = request.args.get('per_page', type=int, default=15)
    parties = party_service.get_parties_for_brand_paginated(
        brand.id, page, per_page
    )

    ticket_count_by_party_id = ticket_service.get_ticket_count_by_party_id()

    return {
        'brand': brand,
        'parties': parties,
        'ticket_count_by_party_id': ticket_count_by_party_id,
    }


@blueprint.route('/parties/<party_id>')
@permission_required(PartyPermission.view)
@templated
def view(party_id):
    """Show a party."""
    party = _get_party_or_404(party_id)
    brand = brand_service.find_brand(party.brand_id)

    days = party_service.get_party_days(party)

    settings = party_settings_service.get_settings(party.id)

    return {
        'brand': brand,
        'party': party,
        'days': days,
        'settings': settings,
    }


@blueprint.route('/for_brand/<brand_id>/create')
@permission_required(PartyPermission.create)
@templated
def create_form(brand_id, erroneous_form=None):
    """Show form to create a party for that brand."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_brand/<brand_id>', methods=['POST'])
@permission_required(PartyPermission.create)
def create(brand_id):
    """Create a party for that brand."""
    brand = _get_brand_or_404(brand_id)

    form = CreateForm(request.form)

    if not form.validate():
        return create_form(brand.id, form)

    party_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    starts_at = local_tz_to_utc(form.starts_at.data)
    ends_at = local_tz_to_utc(form.ends_at.data)
    max_ticket_quantity = form.max_ticket_quantity.data

    party = party_service.create_party(
        party_id,
        brand.id,
        title,
        starts_at,
        ends_at,
        max_ticket_quantity=max_ticket_quantity,
    )

    flash_success(f'Die Party "{party.title}" wurde angelegt.')
    return redirect_to('.index_for_brand', brand_id=brand.id)


@blueprint.route('/parties/<party_id>/update')
@permission_required(PartyPermission.update)
@templated
def update_form(party_id, erroneous_form=None):
    """Show form to update the party."""
    party = _get_party_or_404(party_id)
    brand = brand_service.find_brand(party.brand_id)

    party = dataclasses.replace(
        party,
        starts_at=utc_to_local_tz(party.starts_at),
        ends_at=utc_to_local_tz(party.ends_at),
    )

    form = erroneous_form if erroneous_form else UpdateForm(obj=party)

    return {
        'brand': brand,
        'party': party,
        'form': form,
    }


@blueprint.route('/parties/<party_id>', methods=['POST'])
@permission_required(PartyPermission.update)
def update(party_id):
    """Update a party."""
    party = _get_party_or_404(party_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(party.id, form)

    title = form.title.data.strip()
    starts_at = local_tz_to_utc(form.starts_at.data)
    ends_at = local_tz_to_utc(form.ends_at.data)
    max_ticket_quantity = form.max_ticket_quantity.data
    ticket_management_enabled = form.ticket_management_enabled.data
    seat_management_enabled = form.seat_management_enabled.data
    canceled = form.canceled.data
    archived = form.archived.data

    try:
        party = party_service.update_party(
            party.id,
            title,
            starts_at,
            ends_at,
            max_ticket_quantity,
            ticket_management_enabled,
            seat_management_enabled,
            canceled,
            archived,
        )
    except party_service.UnknownPartyId:
        abort(404, f'Unknown party ID "{party_id}".')

    flash_success(f'Der Party "{party.title}" wurde aktualisiert.')

    return redirect_to('.view', party_id=party.id)


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
