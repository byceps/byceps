"""
byceps.blueprints.admin.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app

from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required


blueprint = create_blueprint('api_admin', __name__)


@blueprint.get('')
@permission_required('api.administrate')
@templated
def index():
    """Show API access status and issued API tokens."""
    api_enabled = current_app.config['API_ENABLED']

    return {
        'api_enabled': api_enabled,
    }
