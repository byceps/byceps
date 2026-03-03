"""
byceps.services.snippet.blueprints.site.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any

from flask import g
from jinja2 import Template
import structlog

from byceps.services.snippet import snippet_service
from byceps.services.snippet.dbmodels import DbSnippetVersion
from byceps.services.snippet.models import SnippetScope
from byceps.util.l10n import get_current_user_locale, get_default_locale
from byceps.util.templating import load_template


log = structlog.get_logger()


Context = dict[str, Any]


def get_rendered_snippet_body(version: DbSnippetVersion) -> str:
    """Return the rendered body of the snippet."""
    template = _load_template_with_globals(version.body)
    return template.render()


def render_snippet_as_partial_from_template(
    name: str,
    *,
    language_code: str | None = None,
    scope: str | None = None,
    ignore_if_unknown: bool = False,
) -> str:
    """Render the latest version of the snippet with the given name and
    return the result.

    This function is meant to be made available in templates.
    """
    language_code = (
        language_code
        or get_current_user_locale()
        or get_default_locale().language
    )
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
    scope: SnippetScope | None = None,
    ignore_if_unknown: bool = False,
    context: Context | None = None,
) -> str:
    """Render the latest version of the snippet with the given name and
    return the result.
    """
    if scope is None:
        scope = SnippetScope.for_site(g.site.id)

    current_version = snippet_service.find_current_version_of_snippet_with_name(
        scope, name, language_code
    )

    if current_version is None:
        if ignore_if_unknown:
            return ''
        else:
            raise SnippetNotFoundException(scope, name, language_code)

    if context is None:
        context = {}

    try:
        return _render_template(current_version.body, context=context)
    except Exception as e:
        log.error(
            'Error in snippet markup',
            scope=scope.as_string(),
            snippet_name=name,
            error=e,
        )
        raise e


def _render_template(source, *, context: Context | None = None) -> str:
    template = _load_template_with_globals(source)

    if context is None:
        context = {}

    return template.render(**context)


def _load_template_with_globals(source: str) -> Template:
    template_globals = {
        'render_snippet': render_snippet_as_partial_from_template,
    }

    return load_template(source, template_globals=template_globals)


class SnippetNotFoundException(Exception):
    def __init__(
        self, scope: SnippetScope, name: str, language_code: str
    ) -> None:
        self.scope = scope
        self.name = name
        self.language_code = language_code
