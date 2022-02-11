"""
Site-specific code extension
"""

from __future__ import annotations
from typing import Any

from flask import g
from flask_babel import get_locale

from byceps.services.ticketing import ticket_service
from byceps.util.l10n import get_locales


def template_context_processor() -> dict[str, Any]:
    """Extend template context."""
    context = {
        'current_locale': get_locale(),
        'locales': get_locales(),
    }

    if g.party_id is not None:
        sale_stats = ticket_service.get_ticket_sale_stats(g.party_id)
        context['ticket_sale_stats'] = sale_stats

    return context
