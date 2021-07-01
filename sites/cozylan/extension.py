"""
Site-specific code extension
"""

from __future__ import annotations
from typing import Any

from flask import g

from byceps.services.seating import seat_service
from byceps.services.ticketing import ticket_service


def template_context_processor() -> dict[str, Any]:
    """Extend template context."""
    context = {}

    if g.party_id is not None:
        sale_stats = ticket_service.get_ticket_sale_stats(g.party_id)
        seat_utilization = seat_service.get_seat_utilization(g.party_id)

        context['ticket_sale_stats'] = sale_stats
        context['seat_utilization'] = seat_utilization

    return context
