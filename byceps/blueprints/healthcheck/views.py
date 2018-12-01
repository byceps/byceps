"""
byceps.blueprints.healthcheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app
from flask.json import dumps

from ...util.framework.blueprint import create_blueprint


blueprint = create_blueprint('healthcheck', __name__)


@blueprint.route('')
def health():
    """Return health status as JSON.

    Adheres to "Health Check Response Format for HTTP APIs"
    (draft-inadarei-api-health-check-03). See
    https://inadarei.github.io/rfc-healthcheck/#rfc.section.3
    for details.
    """
    data = {
        'status': 'ok',
    }

    json = dumps(data) + '\n'

    return current_app.response_class(json, mimetype='application/health+json')
