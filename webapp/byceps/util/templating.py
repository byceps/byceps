# -*- coding: utf-8 -*-

"""
byceps.util.templating
~~~~~~~~~~~~~~~~~~~~~~

Templating utilities.

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from functools import wraps

from flask import render_template


TEMPLATE_FILENAME_EXTENSION = '.html'


def templated(arg):
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
    def decorator(f, template_name=None):
        @wraps(f)
        def decorated(*args, **kwargs):
            name = template_name
            if name is None:
                blueprint_name = f.__module__.split('.')[-2]
                action_name = f.__name__
                name = '{}/{}'.format(blueprint_name, action_name)
            name += TEMPLATE_FILENAME_EXTENSION

            context = f(*args, **kwargs)
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                return context

            return render_template(name, **context)
        return decorated

    if hasattr(arg, '__call__'):
        return decorator(arg)

    def wrapper(f):
        return decorator(f, arg)

    return wrapper
