"""
byceps.blueprints.admin.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import dataclasses
from datetime import date, datetime

from flask import abort, request
from flask_babel import gettext, to_user_timezone, to_utc

from ....services.brand import service as brand_service
from ....services.party import (
    service as party_service,
    settings_service as party_settings_service,
)
from ....services.ticketing import ticket_service
from ....services.ticketing.transfer.models import TicketSaleStats
from ....typing import PartyID
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.iterables import partition
from ....util.views import permission_required, redirect_to

from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('party_admin', __name__)


@blueprint.get('/')
@permission_required('party.view')
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

    days_by_party_id = _get_days_by_party_id(parties)
    ticket_sale_stats_by_party_id = _get_ticket_sale_stats_by_party_id(parties)

    return {
        'parties': parties,
        'active_parties': active_parties,
        'archived_parties': archived_parties,
        'brands': brands,
        'days_by_party_id': days_by_party_id,
        'ticket_sale_stats_by_party_id': ticket_sale_stats_by_party_id,
    }


@blueprint.get('/brands/<brand_id>', defaults={'page': 1})
@blueprint.get('/brands/<brand_id>/pages/<int:page>')
@permission_required('party.view')
@templated
def index_for_brand(brand_id, page):
    """List parties for this brand."""
    brand = _get_brand_or_404(brand_id)

    per_page = request.args.get('per_page', type=int, default=10)
    parties = party_service.get_parties_for_brand_paginated(
        brand.id, page, per_page
    )

    days_by_party_id = _get_days_by_party_id(parties.items)
    ticket_sale_stats_by_party_id = _get_ticket_sale_stats_by_party_id(
        parties.items
    )

    return {
        'brand': brand,
        'parties': parties,
        'per_page': per_page,
        'days_by_party_id': days_by_party_id,
        'ticket_sale_stats_by_party_id': ticket_sale_stats_by_party_id,
    }


def _get_days_by_party_id(parties) -> dict[PartyID, list[date]]:
    return {party.id: party_service.get_party_days(party) for party in parties}


def _get_ticket_sale_stats_by_party_id(
    parties,
) -> dict[PartyID, TicketSaleStats]:
    return {
        party.id: ticket_service.get_ticket_sale_stats(party.id)
        for party in parties
    }


@blueprint.get('/parties/<party_id>')
@permission_required('party.view')
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


@blueprint.get('/for_brand/<brand_id>/create')
@permission_required('party.create')
@templated
def create_form(brand_id, erroneous_form=None):
    """Show form to create a party for that brand."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_brand/<brand_id>')
@permission_required('party.create')
def create(brand_id):
    """Create a party for that brand."""
    brand = _get_brand_or_404(brand_id)

    form = CreateForm(request.form)

    if not form.validate():
        return create_form(brand.id, form)

    party_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    starts_at_local = datetime.combine(form.starts_on.data, form.starts_at.data)
    starts_at_utc = to_utc(starts_at_local)
    ends_at_local = datetime.combine(form.ends_on.data, form.ends_at.data)
    ends_at_utc = to_utc(ends_at_local)
    max_ticket_quantity = form.max_ticket_quantity.data

    party = party_service.create_party(
        party_id,
        brand.id,
        title,
        starts_at_utc,
        ends_at_utc,
        max_ticket_quantity=max_ticket_quantity,
    )

    flash_success(
        gettext('Party "%(title)s" has been created.', title=party.title)
    )

    return redirect_to('.index_for_brand', brand_id=brand.id)


@blueprint.get('/parties/<party_id>/update')
@permission_required('party.update')
@templated
def update_form(party_id, erroneous_form=None):
    """Show form to update the party."""
    party = _get_party_or_404(party_id)
    brand = brand_service.find_brand(party.brand_id)

    starts_at_local = to_user_timezone(party.starts_at)
    ends_at_local = to_user_timezone(party.ends_at)

    data = dataclasses.asdict(party)
    data.update(
        {
            'starts_on': starts_at_local.date(),
            'starts_at': starts_at_local.time(),
            'ends_on': ends_at_local.date(),
            'ends_at': ends_at_local.time(),
        }
    )

    form = erroneous_form if erroneous_form else UpdateForm(data=data)

    return {
        'brand': brand,
        'party': party,
        'form': form,
    }


@blueprint.post('/parties/<party_id>')
@permission_required('party.update')
def update(party_id):
    """Update a party."""
    party = _get_party_or_404(party_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(party.id, form)

    title = form.title.data.strip()
    starts_at_local = datetime.combine(form.starts_on.data, form.starts_at.data)
    starts_at_utc = to_utc(starts_at_local)
    ends_at_local = datetime.combine(form.ends_on.data, form.ends_at.data)
    ends_at_utc = to_utc(ends_at_local)
    max_ticket_quantity = form.max_ticket_quantity.data
    ticket_management_enabled = form.ticket_management_enabled.data
    seat_management_enabled = form.seat_management_enabled.data
    canceled = form.canceled.data
    archived = form.archived.data

    try:
        party = party_service.update_party(
            party.id,
            title,
            starts_at_utc,
            ends_at_utc,
            max_ticket_quantity,
            ticket_management_enabled,
            seat_management_enabled,
            canceled,
            archived,
        )
    except party_service.UnknownPartyId:
        abort(404, f'Unknown party ID "{party_id}".')

    flash_success(
        gettext('Party "%(title)s" has been updated.', title=party.title)
    )

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
