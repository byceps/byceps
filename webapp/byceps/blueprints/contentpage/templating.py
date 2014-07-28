# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import sys
import traceback
import warnings

from flask import abort, render_template, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment


def render_page(name, load_func):
    """Render the page, or an error page if that fails."""
    try:
        context = get_page_context(name, load_func)
        return render_template('contentpage/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in content page markup:', e, file=sys.stderr)
        traceback.print_exc()
        context = {
            'message': str(e),
        }
        return render_template('contentpage/error.html', **context), 500


def get_page_context(name, load_func):
    """Return the page context to insert into the outer template."""
    template = create_env(load_func).get_template(name)

    title, current_page = extract_metadata(name, template)
    body = template.render()

    return {
        'title': title,
        'current_page': current_page,
        'body': body,
    }


def create_env(load_func):
    """Create a sandboxed environment that uses the given function to
    load templates.
    """
    loader = FunctionLoader(load_func)
    env = ImmutableSandboxedEnvironment(
        loader=loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['url_for'] = url_for

    return env


def extract_metadata(id, template):
    """Extract variables from a template."""
    try:
        title = template.module.title
        current_page = template.module.current_page
    except AttributeError:
        warnings.warn(
            'No title and/or current page set for page "{}".'.format(id))
        title = ''
        current_page = None
    return title, current_page
