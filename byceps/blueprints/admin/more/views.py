"""
byceps.blueprints.admin.more.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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
