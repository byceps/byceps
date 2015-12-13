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
from jinja2 import TemplateNotFound

from ...util.templating import get_variable_value, load_template

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
    template = _load_template_with_globals(version.body)

    current_page = get_variable_value(template, 'current_page')
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

    return _render_template(current_version.body)


def _render_template(source):
    template = _load_template_with_globals(source)
    return template.render()


def _load_template_with_globals(source):
    globals = {
        'render_snippet': render_snippet_as_partial,
        'url_for': url_for,
    }
    return load_template(source, globals=globals)
