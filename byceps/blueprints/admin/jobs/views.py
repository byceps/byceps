"""
byceps.blueprints.admin.jobs.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required

from ...common.authorization.registry import permission_registry

from .authorization import JobsPermission


blueprint = create_blueprint('jobs_admin', __name__)


permission_registry.register_enum(JobsPermission)


@blueprint.route('/')
@permission_required(JobsPermission.view)
@templated
def index():
    """Show jobs."""
