"""
byceps.blueprints.admin.more.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from ....services.brand import service as brand_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...common.authorization.decorators import permission_required

from ..core.authorization import AdminPermission


blueprint = create_blueprint('more_admin', __name__)


@blueprint.route('/global')
@permission_required(AdminPermission.access)
@templated
def view_global():
    """Show more global admin items."""
    return {}


@blueprint.route('/brands/<brand_id>')
@permission_required(AdminPermission.access)
@templated
def view_brand(brand_id):
    """Show more brand admin items."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    return {'brand': brand}
