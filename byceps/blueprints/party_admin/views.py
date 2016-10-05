# -*- coding: utf-8 -*-

"""
byceps.blueprints.party_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ...services.party import service as party_service
from ...services.ticket import service as ticket_service
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand import service as brand_service
from ..shop import article_service, order_service

from .authorization import PartyPermission
from .forms import CreateForm


blueprint = create_blueprint('party_admin', __name__)


permission_registry.register_enum(PartyPermission)


@blueprint.route('/')
@permission_required(PartyPermission.list)
@templated
def index():
    """List parties."""
    parties = party_service.get_all_parties_with_brands()

    return {
        'parties': parties,
    }


@blueprint.route('/brands/<brand_id>', defaults={'page': 1})
@blueprint.route('/brands/<brand_id>/pages/<int:page>')
@permission_required(PartyPermission.list)
@templated
def index_for_brand(brand_id, page):
    """List parties for this brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    per_page = request.args.get('per_page', type=int, default=15)
    parties = party_service.get_parties_for_brand_paginated(brand.id, page,
                                                            per_page)

    article_count_by_party_id = article_service.get_article_count_by_party_id()

    order_count_by_party_id = order_service.get_order_count_by_party_id()

    ticket_count_by_party_id = ticket_service.get_ticket_count_by_party_id()

    return {
        'brand': brand,
        'parties': parties,
        'article_count_by_party_id': article_count_by_party_id,
        'order_count_by_party_id': order_count_by_party_id,
        'ticket_count_by_party_id': ticket_count_by_party_id,
    }


@blueprint.route('/<party_id>')
@permission_required(PartyPermission.list)
@templated
def view(party_id):
    """Show a party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    return {
        'party': party,
    }


@blueprint.route('/create')
@permission_required(PartyPermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a party."""
    brands = brand_service.get_brands()

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_brand_choices(brands)

    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
@permission_required(PartyPermission.create)
def create():
    """Create a party."""
    brands = brand_service.get_brands()

    form = CreateForm(request.form)
    form.set_brand_choices(brands)

    if not form.validate():
        return create_form(form)

    brand_id = form.brand_id.data
    brand = brand_service.find_brand(brand_id)
    if not brand:
        flash_error('Unbekannte Marke.')
        return create_form(form)

    party_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    starts_at = form.starts_at.data
    ends_at = form.ends_at.data

    party = party_service.create_party(party_id, brand.id, title, starts_at,
                                       ends_at)

    flash_success('Die Party "{}" wurde angelegt.', party.title)
    return redirect_to('.index')
