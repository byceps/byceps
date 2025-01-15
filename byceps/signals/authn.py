"""
byceps.signals.authn
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


authn_signals = Namespace()


password_updated = authn_signals.signal('password-updated')
user_logged_in = authn_signals.signal('user-logged-in')
