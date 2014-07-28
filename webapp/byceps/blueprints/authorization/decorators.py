# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2006-2014 Jochen Kupperschmidt
"""

from functools import wraps

from flask import abort, g


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
