"""
byceps.signals.user_avatar
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


user_avatar_signals = Namespace()


avatar_updated = user_avatar_signals.signal('user-avatar-updated')
