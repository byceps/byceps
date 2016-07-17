# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..terms.models import Version

from .authorization import TermsPermission


blueprint = create_blueprint('terms_admin', __name__)


permission_registry.register_enum(TermsPermission)


@blueprint.route('/brands/<brand_id>')
@permission_required(TermsPermission.list)
@templated
def index_for_brand(brand_id):
    """List terms versions for that brand."""
    brand = Brand.query.get_or_404(brand_id)

    versions = Version.query \
        .for_brand(brand) \
        .order_by(Version.created_at.desc()) \
        .all()

    return {
        'brand': brand,
        'versions': versions,
    }
