"""
byceps.services.authn.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


authn_signals = Namespace()


password_updated = authn_signals.signal('password-updated')
user_logged_in_to_admin = authn_signals.signal('user-logged-in-to-admin')
user_logged_in_to_site = authn_signals.signal('user-logged-in-to-site')
