"""
byceps.util.views
~~~~~~~~~~~~~~~~~

View utilities.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps

from flask import (
    abort,
    g,
    jsonify,
    redirect,
    request,
    Response,
    stream_with_context,
    url_for,
)
from flask_babel import gettext

from .authz import has_current_user_permission
from .framework.flash import flash_notice


def login_required(func):
    """Ensure the current user has logged in."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user.authenticated:
            flash_notice(gettext('Please log in.'))

            if g.app_mode.is_admin():
                return redirect_to('authn_login_admin.log_in_form', next=request.full_path)
            else:
                return redirect_to('authn_login.log_in_form', next=request.full_path)
        return func(*args, **kwargs)

    return wrapper


def permission_required(permission: str):
    """Ensure the current user has the given permission."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not has_current_user_permission(permission):
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def create_empty_json_response(status):
    """Create a JSON response with the given status code and an empty
    object as its content.
    """
    return Response('{}', status=status, mimetype='application/json')


def jsonified(f):
    """Send the data returned by the decorated function as JSON."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        data = f(*args, **kwargs)
        return jsonify(data)

    return wrapper


def textified(f):
    """Send the data returned by the decorated function as plaintext."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        data = f(*args, **kwargs)
        return Response(stream_with_context(data), mimetype='text/plain')

    return wrapper


def respond_created(f):
    """Send a ``201 Created`` response.

    The decorated callable is expected to return the URL of the newly created
    resource.  That URL is then added to the response as ``Location:`` header.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        url = f(*args, **kwargs)
        return Response(status=201, headers=[('Location', url)])

    return wrapper


def respond_no_content(f):
    """Send a ``204 No Content`` response.

    Optionally, a list of headers may be returned by the decorated callable.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        headers = f(*args, **kwargs)
        return Response(status=204, headers=headers)

    return wrapper


def respond_no_content_with_location(f):
    """Send a ``204 No Content`` response with a 'Location' header."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        location_url = f(*args, **kwargs)
        headers = [('Location', location_url)]
        return Response(status=204, headers=headers)

    return wrapper


def redirect_to(endpoint, **values):
    return redirect(url_for(endpoint, **values))
