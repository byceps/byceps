"""
byceps.signals.auth
~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


auth_signals = Namespace()


user_logged_in = auth_signals.signal('user-logged-in')
