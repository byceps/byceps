"""
byceps.blueprints.snippet.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys
import traceback

from flask import abort, g, render_template, url_for
from jinja2 import TemplateNotFound

from ...services.snippet import service as snippet_service
from ...services.snippet.service import SnippetNotFound
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


def render_snippet_as_partial(name, *, ignore_if_unknown=False):
    """Render the latest version of the snippet with the given name and
    return the result.
    """
    current_version = snippet_service \
        .find_current_version_of_snippet_with_name(g.party_id, name)

    if current_version is None:
        if ignore_if_unknown:
            return ''
        else:
            raise SnippetNotFound('name')

    return _render_template(current_version.body)


def _render_template(source):
    template = _load_template_with_globals(source)
    return template.render()


def _load_template_with_globals(source):
    template_globals = {
        'render_snippet': render_snippet_as_partial,
        'url_for': url_for,
    }

    return load_template(source, template_globals=template_globals)
