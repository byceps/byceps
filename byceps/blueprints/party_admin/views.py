"""
byceps.blueprints.party_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ...services.brand import service as brand_service
from ...services.party import service as party_service
from ...services.shop.article import service as article_service
from ...services.shop.order import service as order_service
from ...services.ticketing import ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import PartyPermission
from .forms import CreateForm, UpdateForm


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
    brand = _get_brand_or_404(brand_id)

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
    party = _get_party_or_404(party_id)

    return {
        'party': party,
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
    starts_at = form.starts_at.data
    ends_at = form.ends_at.data

    party = party_service.create_party(party_id, brand.id, title, starts_at,
                                       ends_at)

    flash_success('Die Party "{}" wurde angelegt.', party.title)
    return redirect_to('.index_for_brand', brand_id=brand.id)


@blueprint.route('/parties/<party_id>/update')
@permission_required(PartyPermission.update)
@templated
def update_form(party_id, erroneous_form=None):
    """Show form to update the party."""
    party = _get_party_or_404(party_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=party)

    return {
        'form': form,
        'party': party,
    }


@blueprint.route('/parties/<party_id>', methods=['POST'])
@permission_required(PartyPermission.update)
def update(party_id):
    """Update a party."""
    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(party_id, form)

    title = form.title.data.strip()
    starts_at = form.starts_at.data
    ends_at = form.ends_at.data
    is_archived = form.is_archived.data

    try:
        party = party_service.update_party(party_id, title, starts_at, ends_at,
                                           is_archived)
    except party_service.UnknownPartyId:
        abort(404, 'Unknown party ID "{}".'.format(party_id))

    flash_success('Der Party "{}" wurde aktualisiert.', party.title)

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
