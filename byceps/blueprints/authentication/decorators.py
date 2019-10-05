"""
byceps.blueprints.authentication.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from functools import wraps

from flask import g

from ...util.framework.flash import flash_notice
from ...util.views import redirect_to


def login_required(func):
    """Ensure the current user has logged in."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.current_user.is_active:
            flash_notice('Bitte melde dich an.')
            return redirect_to('authentication.login_form')
        return func(*args, **kwargs)

    return wrapper
