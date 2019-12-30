"""
byceps.blueprints.snippet.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys
import traceback
from typing import Set

from flask import abort, g, render_template, url_for
from jinja2 import TemplateNotFound

from ...services.snippet import mountpoint_service, service as snippet_service
from ...services.snippet.service import SnippetNotFound
from ...services.snippet.transfer.models import Mountpoint, Scope
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
        'url_for_snippet': url_for_snippet,
    }

    return load_template(source, template_globals=template_globals)


def url_for_snippet(endpoint_suffix: str, **kwargs) -> str:
    """Render an URL pointing to the snippet document's mountpoint."""
    mountpoints = _get_mountpoints()

    # Endpoint suffix is unique per site.
    mountpoints_by_endpoint_suffix = {
        mp.endpoint_suffix: mp for mp in mountpoints
    }

    mountpoint = mountpoints_by_endpoint_suffix[endpoint_suffix]

    return url_for(f'snippet.view', url_path=mountpoint.url_path, **kwargs)


def _get_mountpoints() -> Set[Mountpoint]:
    """Return site-specific mountpoints.

    Preferrably from request-local cache, if available. From the
    database if not yet cached.
    """
    request_context_key = 'snippet_mountpoints'

    mountpoints_from_request_context = g.get(request_context_key)
    if mountpoints_from_request_context:
        return mountpoints_from_request_context
    else:
        mountpoints_from_database = mountpoint_service.get_mountpoints_for_site(g.site_id)
        setattr(g, request_context_key, mountpoints_from_database)
        return mountpoints_from_database
