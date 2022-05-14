"""
byceps.blueprints.site.page.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import sys
import traceback
from typing import Any, Dict, Optional, Union

from flask import abort, render_template
from jinja2 import TemplateNotFound

from ....services.page.transfer.models import Page, Version
from ....util.templating import load_template


Context = Dict[str, Any]


def render_page(page: Page, version: Version) -> Union[str, tuple[str, int]]:
    """Render the page, or an error page if that fails."""
    try:
        context = build_template_context(
            version.title, version.head, version.body
        )
        context['current_page'] = page.name
        return render_template('site/page/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in page markup:', e, file=sys.stderr)
        traceback.print_exc()
        context = {'message': str(e)}
        return render_template('site/page/error.html', **context), 500


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
    template_globals: Context = {}
    template = load_template(source, template_globals=template_globals)
    return template.render()
