# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date
from operator import attrgetter

from flask import g, request

from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..news.models import Item
from ..news import service
from ..news import signals
from ..party.models import Party

from .authorization import NewsItemPermission
from .forms import ItemCreateForm, ItemUpdateForm


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


@blueprint.route('/brands/<brand_id>', defaults={'page': 1})
@blueprint.route('/brands/<brand_id>/pages/<int:page>')
@permission_required(NewsItemPermission.list)
@templated
def index_for_brand(brand_id, page):
    """List news items for that brand."""
    brand = get_brand_or_404(brand_id)

    per_page = request.args.get('per_page', type=int, default=15)
    query = Item.query \
        .for_brand(brand) \
        .with_current_version() \
        .order_by(Item.published_at.desc())

    items = query.paginate(page, per_page)

    return {
        'brand': brand,
        'items': items,
    }


@blueprint.route('/for_brand/<brand_id>/create')
@permission_required(NewsItemPermission.create)
@templated
def create_form(brand_id, *, erroneous_form=None):
    """Show form to create a news item."""
    brand = get_brand_or_404(brand_id)

    if erroneous_form:
        form = erroneous_form
    else:
        slug_prefix = date.today().strftime('%Y-%m-%d-')
        form = ItemCreateForm(slug=slug_prefix)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_brand/<brand_id>', methods=['POST'])
@permission_required(NewsItemPermission.create)
def create(brand_id):
    """Create a news item."""
    brand = get_brand_or_404(brand_id)

    form = ItemCreateForm(request.form)

    slug = form.slug.data.strip().lower()
    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    item = service.create_item(brand, slug, creator, title, body,
        image_url_path=image_url_path)

    flash_success('Die News "{}" wurde angelegt.', item.title)
    signals.item_published.send(None, item=item)

    return redirect_to('.index_for_brand', brand_id=brand.id)


@blueprint.route('/items/<uuid:id>/update')
@permission_required(NewsItemPermission.update)
@templated
def update_form(id):
    """Show form to update a news item."""
    item = Item.query.get_or_404(id)

    form = ItemUpdateForm(obj=item.current_version, slug=item.slug)

    return {
        'item': item,
        'form': form,
    }


@blueprint.route('/items/<uuid:id>', methods=['POST'])
@permission_required(NewsItemPermission.update)
def update(id):
    """Update a news item."""
    item = Item.query.get_or_404(id)

    form = ItemUpdateForm(request.form)

    slug = form.slug.data.strip().lower()
    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    service.update_item(item, creator, title, body,
                        image_url_path=image_url_path)

    flash_success('Die News "{}" wurde aktualisiert.', item.title)
    return redirect_to('.index_for_brand', brand_id=item.brand.id)


def get_brand_or_404(brand_id):
    return Brand.query.get_or_404(brand_id)
