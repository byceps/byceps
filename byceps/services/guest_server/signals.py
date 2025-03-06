"""
byceps.services.guest_server.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


guest_server_signals = Namespace()


# fmt: off
guest_server_registered = guest_server_signals.signal('guest-server-registered')
guest_server_approved = guest_server_signals.signal('guest-server-approved')
guest_server_checked_in = guest_server_signals.signal('guest-server-checked-in')
guest_server_checked_out = guest_server_signals.signal('guest-server-checked-out')
# fmt: on
