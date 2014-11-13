# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from .models import Ticket


def find_ticket_for_user(user, party):
    """Return the ticket used by the user for the party, or `None` if not
    found.
    """
    return Ticket.query \
        .filter(Ticket.used_by == user) \
        .for_party(party) \
        .first()
