# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys
import traceback
import warnings

from flask import abort, render_template, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment

from .service import get_current_version_of_snippet_with_name, SnippetNotFound


def render_snippet_as_page(version):
    """Render the given version of the snippet, or an error page if
    that fails.
    """
    try:
        context = get_snippet_context(version)
        return render_template('snippet/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in snippet markup:', e, file=sys.stderr)
        traceback.print_exc()
        context = {
            'message': str(e),
        }
        return render_template('snippet/error.html', **context), 500


def get_snippet_context(version):
    """Return the snippet context to insert into the outer template."""
    template = load_template(version)

    current_page = extract_variable(template, 'current_page')
    title = version.title
    body = template.render()

    return {
        'title': title,
        'current_page': current_page,
        'body': body,
    }


def render_snippet_as_partial(name, *, ignore_if_unknown=False):
    """Render the latest version of the snippet with the given name and
    return the result.
    """
    try:
        current_version = get_current_version_of_snippet_with_name(name)
    except SnippetNotFound as e:
        if ignore_if_unknown:
            return ''
        else:
            raise e

    return render_body(current_version)


def render_body(version):
    """Render the snippet version's body as a template."""
    template = load_template(version)
    return template.render()


def load_template(version):
    """Load the template from the snippet version's body."""
    env = create_env()
    return env.from_string(version.body)


def create_env():
    """Create a sandboxed environment that uses the given function to
    load templates.
    """
    dummy_loader = FunctionLoader(lambda name: None)
    env = ImmutableSandboxedEnvironment(
        loader=dummy_loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['render_snippet'] = render_snippet_as_partial
    env.globals['url_for'] = url_for

    return env


def extract_variable(template, name):
    """Try to extract a variable's value from the template, or return
    `None` if the variable is not defined.
    """
    try:
        return getattr(template.module, name)
    except AttributeError:
        return None
