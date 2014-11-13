# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from .models import Ticket


def find_current_party_ticket_for_user(user):
    """Return the ticket used by the user for the current party, or
    `None` if not found.
    """
    return Ticket.query \
        .for_current_party() \
        .filter(Ticket.used_by == user) \
        .first()
