# -*- coding: utf-8 -*-

"""
byceps.blueprints.party_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import request

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..party.models import Party

from .authorization import PartyPermission
from .forms import CreateForm


blueprint = create_blueprint('party_admin', __name__)


permission_registry.register_enum(PartyPermission)


@blueprint.route('/')
@permission_required(PartyPermission.list)
@templated
def index():
    """List parties."""
    parties = Party.query.options(db.joinedload('brand')).all()
    return {'parties': parties}


@blueprint.route('/brands/<brand_id>', defaults={'page': 1})
@blueprint.route('/brands/<brand_id>/pages/<int:page>')
@permission_required(PartyPermission.list)
@templated
def index_for_brand(brand_id, page):
    """List parties for this brand."""
    brand = Brand.query.get_or_404(brand_id)

    per_page = request.args.get('per_page', type=int, default=15)

    parties = Party.query.for_brand(brand).paginate(page, per_page)

    return {
        'brand': brand,
        'parties': parties,
    }


@blueprint.route('/<id>')
@permission_required(PartyPermission.list)
@templated
def view(id):
    """Show a party."""
    party = Party.query.get_or_404(id)

    return {
        'party': party,
    }


@blueprint.route('/create')
@permission_required(PartyPermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a party."""
    brands = get_brands_by_title()

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_brand_choices(brands)

    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
@permission_required(PartyPermission.create)
def create():
    """Create a party."""
    brands = get_brands_by_title()

    form = CreateForm(request.form)
    form.set_brand_choices(brands)

    if not form.validate():
        return create_form(form)

    brand_id = form.brand_id.data
    brand = Brand.query.get(brand_id)
    if not brand:
        flash_error('Unbekannte Marke.')
        return create_form(form)

    id = form.id.data.strip().lower()
    title = form.title.data.strip()
    starts_at = form.starts_at.data
    ends_at = form.ends_at.data

    party = Party(id, brand, title, starts_at, ends_at)
    db.session.add(party)
    db.session.commit()

    flash_success('Die Party "{}" wurde angelegt.', party.title)
    return redirect_to('.index')


def get_brands_by_title():
    return Brand.query.order_by(Brand.title).all()
