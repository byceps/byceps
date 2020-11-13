"""
byceps.blueprints.common.authorization.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps

from flask import abort, g


def permission_required(permission):
    """Ensure the current user has the given permission."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not g.current_user.has_permission(permission):
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
