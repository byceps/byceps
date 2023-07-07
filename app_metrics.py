"""
metrics application instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os

from byceps.config import ConfigurationError
from byceps.metrics.application import create_metrics_app


ENV_VAR_NAME_DATABASE_URI = 'DATABASE_URI'


database_uri = os.environ.get(ENV_VAR_NAME_DATABASE_URI)
if not database_uri:
    raise ConfigurationError(
        f"No database URI was specified via the '{ENV_VAR_NAME_DATABASE_URI}' "
        "environment variable.",
    )

app = create_metrics_app(database_uri)
