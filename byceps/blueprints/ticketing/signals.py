"""
byceps.blueprints.ticketing.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


ticketing_signals = Namespace()


ticket_checked_in = ticketing_signals.signal('ticket-checked-in')
