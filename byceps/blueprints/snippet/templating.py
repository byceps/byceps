"""
byceps.blueprints.snippet.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys
import traceback

from flask import abort, g, render_template, url_for
from jinja2 import TemplateNotFound

from ...services.snippet import service as snippet_service
from ...services.snippet.service import SnippetNotFound
from ...services.snippet.transfer.models import Scope
from ...util.templating import get_variable_value, load_template


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
    head = _render_template(version.head) if version.head else None
    body = template.render()

    return {
        'title': title,
        'current_page': current_page,
        'head': head,
        'body': body,
    }


def render_snippet_as_partial(
    name, *, scope=None, ignore_if_unknown=False, context=None
):
    """Render the latest version of the snippet with the given name and
    return the result.
    """
    if scope is None:
        scope = Scope.for_site(g.site_id)

    current_version = snippet_service.find_current_version_of_snippet_with_name(
        scope, name
    )

    if current_version is None:
        if ignore_if_unknown:
            return ''
        else:
            raise SnippetNotFound(scope, name)

    if context is None:
        context = {}

    return _render_template(current_version.body, context=context)


def _render_template(source, *, context=None):
    template = _load_template_with_globals(source)

    if context is None:
        context = {}

    return template.render(**context)


def _load_template_with_globals(source):
    template_globals = {
        'render_snippet': render_snippet_as_partial,
        'url_for': url_for,
    }

    return load_template(source, template_globals=template_globals)
