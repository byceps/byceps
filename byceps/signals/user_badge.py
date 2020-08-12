"""
byceps.signals.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


user_badge_signals = Namespace()


user_badge_awarded = user_badge_signals.signal('user-badge-awarded')
