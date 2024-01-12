"""
byceps.signals.orga
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


orga_signals = Namespace()


orga_status_granted = orga_signals.signal('orga-status-granted')
orga_status_revoked = orga_signals.signal('orga-status-revoked')
