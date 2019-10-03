"""
byceps.blueprints.admin.brand.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ....services.brand import (
    service as brand_service,
    settings_service as brand_settings_service,
)
from ....services.news import service as news_service
from ....services.orga import service as orga_service
from ....services.party import service as party_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import BrandPermission
from .forms import CreateForm


blueprint = create_blueprint('brand_admin', __name__)


permission_registry.register_enum(BrandPermission)


@blueprint.route('/')
@permission_required(BrandPermission.view)
@templated
def index():
    """List brands."""
    brands = brand_service.get_brands()

    party_count_by_brand_id = party_service.get_party_count_by_brand_id()

    orga_count_by_brand_id = orga_service.get_person_count_by_brand_id()

    news_item_count_by_brand_id = news_service.get_item_count_by_brand_id()

    return {
        'brands': brands,
        'party_count_by_brand_id': party_count_by_brand_id,
        'orga_count_by_brand_id': orga_count_by_brand_id,
        'news_item_count_by_brand_id': news_item_count_by_brand_id,
    }


@blueprint.route('/create')
@permission_required(BrandPermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a brand."""
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
@permission_required(BrandPermission.create)
def create():
    """Create a brand."""
    form = CreateForm(request.form)

    if not form.validate():
        return create_form(form)

    brand_id = form.id.data.strip().lower()
    title = form.title.data.strip()

    brand = brand_service.create_brand(brand_id, title)

    flash_success('Die Marke "{}" wurde angelegt.', brand.title)
    return redirect_to('.index')


@blueprint.route('/brands/<brand_id>')
@permission_required(BrandPermission.view)
@templated
def view(brand_id):
    """Show a brand."""
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    settings = brand_settings_service.get_settings(brand.id)

    return {
        'brand': brand,
        'settings': settings,
    }
