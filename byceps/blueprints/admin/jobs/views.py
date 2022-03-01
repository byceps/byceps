"""
byceps.blueprints.admin.jobs.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required


blueprint = create_blueprint('jobs_admin', __name__)


@blueprint.get('/')
@permission_required('jobs.view')
@templated
def index():
    """Show jobs."""
