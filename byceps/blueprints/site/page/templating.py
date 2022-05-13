"""
byceps.blueprints.site.page.templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from ....util.templating import load_template


Context = Dict[str, Any]


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
