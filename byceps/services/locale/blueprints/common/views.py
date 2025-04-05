"""
byceps.services.locale.blueprints.common.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import redirect, request

from byceps.util import user_session
from byceps.util.framework.blueprint import create_blueprint


blueprint = create_blueprint('locale', __name__)


@blueprint.get('/set')
def set_locale():
    """Set the locale."""
    locale = request.args.get('locale')
    user_session.set_locale(locale)
    return redirect('/')
