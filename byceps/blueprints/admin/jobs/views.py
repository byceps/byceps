"""
byceps.blueprints.admin.jobs.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import JobsPermission


blueprint = create_blueprint('jobs_admin', __name__)


permission_registry.register_enum(JobsPermission)


@blueprint.route('/')
@permission_required(JobsPermission.view)
@templated
def index():
    """Show jobs."""
