"""
byceps.signals.auth
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


auth_signals = Namespace()


password_updated = auth_signals.signal('password-updated')
user_logged_in = auth_signals.signal('user-logged-in')
