"""
byceps.blueprints.monitoring.metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Metrics export for `Prometheus <https://prometheus.io/>`_

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Response

from ....services.metrics import service as metrics_service
from ....util.framework.blueprint import create_blueprint


blueprint = create_blueprint('metrics', __name__)


@blueprint.get('')
def metrics():
    """Return metrics."""
    metrics = metrics_service.collect_metrics()
    lines = list(metrics_service.serialize(metrics))

    return Response(lines, status=200, mimetype='text/plain; version=0.0.4')
