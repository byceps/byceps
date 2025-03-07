"""
byceps.services.ticketing.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


ticketing_signals = Namespace()


ticket_checked_in = ticketing_signals.signal('ticket-checked-in')
tickets_sold = ticketing_signals.signal('tickets-sold')
