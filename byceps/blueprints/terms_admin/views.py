"""
byceps.blueprints.terms_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ...services.brand import service as brand_service
from ...services.terms import service as terms_service
from ...util.framework.blueprint import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import TermsPermission


blueprint = create_blueprint('terms_admin', __name__)


permission_registry.register_enum(TermsPermission)


@blueprint.route('/brands/<brand_id>')
@permission_required(TermsPermission.list)
@templated
def index_for_brand(brand_id):
    """List terms versions for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    versions = terms_service.get_versions_for_brand(brand.id)

    current_version_id = terms_service.find_current_version_id(brand.id)

    return {
        'brand': brand,
        'versions': versions,
        'current_version_id': current_version_id,
    }
