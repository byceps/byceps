# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import g, request

from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..news.models import CurrentVersionAssociation, Item, ItemVersion
from ..news import service
from ..news import signals
from ..party.models import Party
from ..snippet.models.snippet import Snippet

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
    brand = get_brand_or_404(brand_id)
    items = Item.query.for_brand(brand).with_current_version().all()
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

    form = erroneous_form if erroneous_form else ItemCreateForm()

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


def get_brand_or_404(brand_id):
    return Brand.query.get_or_404(brand_id)
