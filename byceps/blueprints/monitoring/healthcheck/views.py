"""
byceps.blueprints.monitoring.healthcheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app
from flask.json import dumps

from sqlalchemy.exc import OperationalError

from ....database import db
from ....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('healthcheck', __name__)


@blueprint.route('')
def health():
    """Return health status as JSON.

    Adheres to "Health Check Response Format for HTTP APIs"
    (draft-inadarei-api-health-check-03). See
    https://inadarei.github.io/rfc-healthcheck/#rfc.section.3
    for details.
    """
    rdbms_ok = _is_rdbms_ok()

    data = {
        'status': 'ok',
        'details': {
            'rdbms': [
                {
                    'status': 'ok' if rdbms_ok else 'fail',
                },
            ],
        },
    }

    json = dumps(data) + '\n'
    status_code = 503 if not rdbms_ok else 200

    return current_app.response_class(
        json, status=status_code, content_type='application/health+json'
    )


def _is_rdbms_ok():
    try:
        db.session.execute('SELECT 1')
        return True
    except OperationalError:
        return False
