"""
byceps.blueprints.admin.jobs.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, Flask
import rq_dashboard

from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required

from byceps.util.authz import has_current_user_permission


blueprint = create_blueprint('jobs_admin', __name__)


@rq_dashboard.blueprint.before_request
def require_permission() -> None:
    if not has_current_user_permission('jobs.view'):
        abort(403)


def enable_rq_dashboard(app: Flask, url_prefix: str) -> None:
    rq_dashboard.web.setup_rq_connection(app)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix=url_prefix)


@blueprint.get('/')
@permission_required('jobs.view')
@templated
def index():
    """Show jobs."""
