"""
byceps.blueprints.site.snippet.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from flask import g
from jinja2 import Template

from ....services.snippet.dbmodels.snippet import SnippetVersion
from ....services.snippet import service as snippet_service
from ....services.snippet.service import SnippetNotFound
from ....services.snippet.transfer.models import Scope
from ....util.templating import load_template


Context = Dict[str, Any]


def get_snippet_context(version: SnippetVersion) -> Context:
    """Return the snippet context to insert into the outer template."""
    template = _load_template_with_globals(version.body)

    title = version.title
    head = _render_template(version.head) if version.head else None
    body = template.render()

    return {
        'page_title': title,
        'head': head,
        'body': body,
    }


def render_snippet_as_partial_from_template(
    name: str,
    *,
    scope: Optional[str] = None,
    ignore_if_unknown: bool = False,
) -> str:
    """Render the latest version of the snippet with the given name and
    return the result.

    This function is meant to be made available in templates.
    """
    scope_obj = _parse_scope_string(scope) if (scope is not None) else None

    return render_snippet_as_partial(
        name, scope=scope_obj, ignore_if_unknown=ignore_if_unknown
    )


def _parse_scope_string(value: str) -> Scope:
    """Parse a slash-separated string into a scope object."""
    type_, name = value.partition('/')[::2]
    return Scope(type_, name)


def render_snippet_as_partial(
    name: str,
    *,
    scope: Optional[Scope] = None,
    ignore_if_unknown: bool = False,
    context: Optional[Context] = None,
) -> str:
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


def _render_template(source, *, context: Optional[Context] = None) -> str:
    template = _load_template_with_globals(source)

    if context is None:
        context = {}

    return template.render(**context)


def _load_template_with_globals(source: str) -> Template:
    template_globals = {
        'render_snippet': render_snippet_as_partial_from_template,
    }

    return load_template(source, template_globals=template_globals)
