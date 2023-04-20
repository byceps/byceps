"""
byceps.blueprints.site.page.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

import sys
import traceback
from typing import Any, Optional

from flask import abort, g, render_template, url_for
from jinja2 import TemplateNotFound

from byceps.blueprints.site.snippet.templating import render_snippet_as_partial_from_template
from byceps.services.page import page_service
from byceps.services.page.models import Page, PageVersion
from byceps.services.site_navigation import site_navigation_service
from byceps.services.site_navigation.models import NavMenuID
from byceps.util.l10n import get_default_locale, get_locale_str
from byceps.util.templating import load_template


Context = dict[str, Any]


def render_page(page: Page, version: PageVersion) -> str | tuple[str, int]:
    """Render the page, or an error page if that fails."""
    try:
        context = build_template_context(
            version.title, version.head, version.body
        )
        context['current_page'] = page.current_page_id

        subnav_menu_id = _find_subnav_menu_id(page)
        if subnav_menu_id:
            context['subnav_menu_id'] = subnav_menu_id

        return render_template('site/page/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in page markup:', e, file=sys.stderr)
        traceback.print_exc()
        context = {'message': str(e)}
        return render_template('site/page/error.html', **context), 500


def _find_subnav_menu_id(page: Page) -> Optional[NavMenuID]:
    if page.nav_menu_id:
        return page.nav_menu_id

    language_code = get_locale_str() or get_default_locale()
    return site_navigation_service.find_submenu_id_for_page(
        g.site_id, language_code, page.name
    )


def build_template_context(
    title: str, raw_head: Optional[str], raw_body: str
) -> Context:
    """Build the page context to insert into the outer template."""
    head = _render_template(raw_head) if raw_head else None
    body = _render_template(raw_body)

    return {
        'page_title': title,
        'head': head,
        'body': body,
    }


def _render_template(source: str) -> str:
    template_globals: Context = {
        'render_snippet': render_snippet_as_partial_from_template,
        'url_for_page': url_for_page,
    }

    template = load_template(source, template_globals=template_globals)
    return template.render()


def url_for_page(name: str, **kwargs) -> Optional[str]:
    """Render an URL pointing to the page's URL path."""
    site_id = getattr(g, 'site_id', None)
    if site_id is None:
        return None

    return url_for_site_page(site_id, name, **kwargs)


def url_for_site_page(site_id: str, name: str, **kwargs) -> str:
    """Render an URL pointing to the page's URL path."""
    # Page name is unique per site.

    url_paths_by_page_name = _get_url_paths_by_page_name(site_id)

    url_path = url_paths_by_page_name[name]

    return url_for('page.view', url_path=url_path, **kwargs)


def _get_url_paths_by_page_name(site_id) -> dict[str, str]:
    """Return site-specific mapping from page names to URL paths.

    Preferrably from request-local cache, if available. From the
    database if not yet cached.
    """
    request_context_key = f'page_url_paths_by_page_name_for_site_{site_id}'

    url_paths_by_page_name_from_request_context = g.get(request_context_key)
    if url_paths_by_page_name_from_request_context:
        return url_paths_by_page_name_from_request_context
    else:
        url_paths_by_page_name_from_database = (
            page_service.get_url_paths_by_page_name_for_site(site_id)
        )
        setattr(g, request_context_key, url_paths_by_page_name_from_database)
        return url_paths_by_page_name_from_database
