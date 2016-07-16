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
from ..brand.models import Brand

from .authorization import BrandPermission


blueprint = create_blueprint('brand_admin', __name__)


permission_registry.register_enum(BrandPermission)


@blueprint.route('/')
@permission_required(BrandPermission.view)
@templated
def index():
    """List brands."""
    brands = Brand.query.order_by(Brand.title).all()

    return {
        'brands': brands,
    }
