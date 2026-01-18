"""
byceps.services.user_badge.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


user_badge_signals = Namespace()


user_badge_awarded = user_badge_signals.signal('user-badge-awarded')
