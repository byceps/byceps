"""
byceps.services.orga.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


orga_signals = Namespace()


orga_status_granted = orga_signals.signal('orga-status-granted')
orga_status_revoked = orga_signals.signal('orga-status-revoked')
