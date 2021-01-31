"""
byceps.blueprints.admin.maintenance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required

from ..core.authorization import AdminPermission


blueprint = create_blueprint('maintenance_admin', __name__)


@blueprint.route('')
@permission_required(AdminPermission.access)
@templated
def index():
    """Show maintenance overview."""
    return {}
