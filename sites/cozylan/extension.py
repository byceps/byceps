"""
Site-specific code extension
"""

from __future__ import annotations
from typing import Any

from flask import g
from flask_babel import get_locale

from byceps.services.seating import seat_service
from byceps.services.ticketing import ticket_service
from byceps.util.l10n import get_locales


_LOCALE_ICONS_BY_CODE = {
    'en': '🇬🇧',
    'de': '🇩🇪',
}


def template_context_processor() -> dict[str, Any]:
    """Extend template context."""
    context = {
        'current_locale': get_locale(),
        'locales': get_locales(),
        'locale_icons_by_code': _LOCALE_ICONS_BY_CODE,
    }

    if g.party_id is not None:
        sale_stats = ticket_service.get_ticket_sale_stats(g.party_id)
        seat_utilization = seat_service.get_seat_utilization(g.party_id)

        context['ticket_sale_stats'] = sale_stats
        context['seat_utilization'] = seat_utilization

    return context
