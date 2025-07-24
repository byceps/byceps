"""
byceps.services.seating.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


seating_signals = Namespace()


seat_group_occupied = seating_signals.signal('seat-group-occupied')
seat_group_released = seating_signals.signal('seat-group-released')
