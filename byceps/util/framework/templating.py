"""
byceps.util.framework.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Templating utilities

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import render_template


_TEMPLATE_FILENAME_EXTENSION = '.html'


def templated(arg) -> Callable:
    """Decorate a callable to wrap its return value in a template and that in
    a response object.

    This decorator expects the decorated callable to return a dictionary of
    objects that should be added to the template context, or ``None``.

    The name of the template to render can be either specified as argument or,
    if not present, will be determined by concatenating the callable's module
    and function object name (format: 'module_callable').

    The rendered template string will be wrapped in a ``Response`` object and
    returned.
    """

    if hasattr(arg, '__call__'):
        return _decorate(arg)

    def wrapper(f: Callable):
        return _decorate(f, arg)

    return wrapper


def _decorate(f: Callable, template_name: str | None = None) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        name = _get_template_name(f, template_name)

        context = f(*args, **kwargs)

        if context is None:
            context = {}
        elif not isinstance(context, dict):
            return context

        return render_template(name, **context)

    return decorated


def _get_template_name(
    view_function: Callable, template_name: str | None
) -> str:
    if template_name is None:
        name = _derive_template_name(view_function)
    else:
        name = template_name

    return name + _TEMPLATE_FILENAME_EXTENSION


def _derive_template_name(view_function: Callable) -> str:
    """Derive the template name from the view function's module and name."""
    # Select segments between `byceps.blueprints.` and `.views`.
    module_package_name_segments = view_function.__module__.split('.')
    blueprint_path_segments = module_package_name_segments[2:-1]

    action_name = view_function.__name__

    return '/'.join(blueprint_path_segments + [action_name])
