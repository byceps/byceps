# -*- coding: utf-8 -*-

"""
byceps.blueprints.brand_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand import service as brand_service
from ..news_admin import service as news_admin_service
from ..orga_admin import service as orga_admin_service
from ..party import service as party_service

from .authorization import BrandPermission


blueprint = create_blueprint('brand_admin', __name__)


permission_registry.register_enum(BrandPermission)


@blueprint.route('/')
@permission_required(BrandPermission.view)
@templated
def index():
    """List brands."""
    brands = brand_service.get_brands()

    party_count_by_brand_id = party_service.get_party_count_by_brand_id()

    orga_count_by_brand_id = orga_admin_service \
        .get_person_count_by_brand_id()

    news_item_count_by_brand_id = news_admin_service \
        .get_item_count_by_brand_id()

    return {
        'brands': brands,
        'party_count_by_brand_id': party_count_by_brand_id,
        'orga_count_by_brand_id': orga_count_by_brand_id,
        'news_item_count_by_brand_id': news_item_count_by_brand_id,
    }
