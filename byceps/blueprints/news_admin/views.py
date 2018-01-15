"""
byceps.blueprints.news_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from flask import abort, g, request

from ...services.brand import service as brand_service
from ...services.news import service as news_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..news import signals

from .authorization import NewsItemPermission
from .forms import ItemCreateForm, ItemUpdateForm


blueprint = create_blueprint('news_admin', __name__)


permission_registry.register_enum(NewsItemPermission)


@blueprint.route('/brands/<brand_id>', defaults={'page': 1})
@blueprint.route('/brands/<brand_id>/pages/<int:page>')
@permission_required(NewsItemPermission.list)
@templated
def index_for_brand(brand_id, page):
    """List news items for that brand."""
    brand = get_brand_or_404(brand_id)

    per_page = request.args.get('per_page', type=int, default=15)

    items = news_service.get_items_paginated(brand.id, page, per_page)

    return {
        'brand': brand,
        'items': items,
    }


@blueprint.route('/versions/<uuid:version_id>')
@permission_required(NewsItemPermission.list)
@templated
def view_version(version_id):
    """Show the news item with the given version."""
    version = news_service.find_item_version(version_id)

    return {
        'version': version,
    }


@blueprint.route('/for_brand/<brand_id>/create')
@permission_required(NewsItemPermission.create)
@templated
def create_form(brand_id, erroneous_form=None):
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
    if not form.validate():
        return create_form(brand.id, form)

    slug = form.slug.data.strip().lower()
    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    item = news_service.create_item(brand.id, slug, creator.id, title, body,
                                    image_url_path=image_url_path)

    flash_success('Die News "{}" wurde angelegt.', item.title)
    signals.item_published.send(None, item_id=item.id)

    return redirect_to('.index_for_brand', brand_id=brand.id)


@blueprint.route('/items/<uuid:item_id>/update')
@permission_required(NewsItemPermission.update)
@templated
def update_form(item_id, erroneous_form=None):
    """Show form to update a news item."""
    item = get_item_or_404(item_id)

    form = erroneous_form if erroneous_form \
            else ItemUpdateForm(obj=item.current_version, slug=item.slug)

    return {
        'item': item,
        'form': form,
    }


@blueprint.route('/items/<uuid:item_id>', methods=['POST'])
@permission_required(NewsItemPermission.update)
def update(item_id):
    """Update a news item."""
    item = get_item_or_404(item_id)

    form = ItemUpdateForm(request.form)
    if not form.validate():
        return update_form(item.id, form)

    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    news_service.update_item(item, creator.id, title, body,
                             image_url_path=image_url_path)

    flash_success('Die News "{}" wurde aktualisiert.', item.title)
    return redirect_to('.index_for_brand', brand_id=item.brand.id)


def get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def get_item_or_404(item_id):
    item = news_service.find_item(item_id)

    if item is None:
        abort(404)

    return item
