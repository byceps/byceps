"""
byceps.blueprints.monitoring.healthcheck
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app
from flask.json import dumps
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from byceps.database import db
from byceps.util.framework.blueprint import create_blueprint


blueprint = create_blueprint('healthcheck', __name__)


@blueprint.get('')
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
        db.session.execute(text('SELECT 1'))
        return True
    except OperationalError:
        return False
