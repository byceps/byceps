"""
byceps.blueprints.site.snippet.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Optional

from flask import g
from jinja2 import Template

from ....services.snippet.dbmodels import DbSnippetVersion
from ....services.snippet.models import SnippetScope
from ....services.snippet import snippet_service
from ....util.l10n import get_user_locale
from ....util.templating import load_template


Context = dict[str, Any]


def get_rendered_snippet_body(version: DbSnippetVersion) -> str:
    """Return the rendered body of the snippet."""
    template = _load_template_with_globals(version.body)
    return template.render()


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
    language_code = get_user_locale(g.user)
    scope_obj = _parse_scope_string(scope) if (scope is not None) else None

    return render_snippet_as_partial(
        name,
        language_code,
        scope=scope_obj,
        ignore_if_unknown=ignore_if_unknown,
    )


def _parse_scope_string(value: str) -> SnippetScope:
    """Parse a slash-separated string into a scope object."""
    type_, name = value.partition('/')[::2]
    return SnippetScope(type_, name)


def render_snippet_as_partial(
    name: str,
    language_code: str,
    *,
    scope: Optional[SnippetScope] = None,
    ignore_if_unknown: bool = False,
    context: Optional[Context] = None,
) -> str:
    """Render the latest version of the snippet with the given name and
    return the result.
    """
    if scope is None:
        scope = SnippetScope.for_site(g.site_id)

    current_version = snippet_service.find_current_version_of_snippet_with_name(
        scope, name, language_code
    )

    if current_version is None:
        if ignore_if_unknown:
            return ''
        else:
            raise snippet_service.SnippetNotFound(scope, name, language_code)

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
