"""
byceps.blueprints.user_avatar.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


user_avatar_signals = Namespace()


avatar_updated = user_avatar_signals.signal('avatar-updated')
