# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import request

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..news.models import Item
from ..snippet.models import Snippet

from .authorization import NewsItemPermission
from .forms import ItemCreateForm


blueprint = create_blueprint('news_admin', __name__)


permission_registry.register_enum(NewsItemPermission)


@blueprint.route('/')
@permission_required(NewsItemPermission.list)
@templated
def index():
    """List brands to choose from."""
    brands = Brand.query.all()
    return {
        'brands': brands,
    }


@blueprint.route('/<brand_id>')
@permission_required(NewsItemPermission.list)
@templated
def index_for_brand(brand_id):
    """List news items for that brand."""
    brand = Brand.query.get_or_404(brand_id)
    items = Item.query.for_brand(brand) \
        .options(
            db.joinedload_all('snippet.current_version_association.version'),
        ) \
        .all()
    return {
        'brand': brand,
        'items': items,
    }


@blueprint.route('/for_brand/<brand_id>/create')
@permission_required(NewsItemPermission.create)
@templated
def create_form(brand_id, *, erroneous_form=None):
    """Show form to create a news item."""
    brand = Brand.query.get_or_404(brand_id)
    form = erroneous_form if erroneous_form else ItemCreateForm()
    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_brand/<brand_id>', methods=['POST'])
@permission_required(NewsItemPermission.create)
def create(brand_id):
    """Create a news item."""
    brand = Brand.query.get_or_404(brand_id)
    form = ItemCreateForm(request.form)

    slug = form.slug.data.strip().lower()
    snippet_id = form.snippet_id.data.strip()

    snippet = Snippet.query.get(snippet_id)
    if not snippet:
        flash_error('Es wurde kein Snippet mit der ID "{}" gefunden.',
                    snippet_id)
        return create_form(brand.id, erroneous_form=form)

    if snippet.party.brand != brand:
        flash_error('Das Snippet gehört nicht zur Marke "{}".', brand.title)
        return create_form(brand.id, erroneous_form=form)

    item = Item(brand=brand, slug=slug, snippet=snippet)
    db.session.add(item)
    db.session.commit()

    flash_success('Die News "{}" wurde angelegt.', item.title)
    return redirect_to('.index_for_brand', brand_id=brand.id)
