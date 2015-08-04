# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from functools import wraps

from flask import abort, g

from ...util.views import redirect_to


def login_required(func):
    """Ensure the current user has logged in."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.current_user.is_active:
            return redirect_to('user.login_form')
        return func(*args, **kwargs)
    return wrapper


def permission_required(permission):
    """Ensure the current user has the given permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if permission not in g.current_user.permissions:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def role_required(role):
    """Ensure the current user has the given role."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if role not in g.current_user.roles:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
