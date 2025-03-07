"""
byceps.services.user.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


user_signals = Namespace()


avatar_updated = user_signals.signal('user-avatar-updated')
details_updated = user_signals.signal('user-details-updated')
email_address_changed = user_signals.signal('email-address-changed')
email_address_confirmed = user_signals.signal('email-address-confirmed')
email_address_invalidated = user_signals.signal('email-address-invalidated')
account_created = user_signals.signal('user-account-created')
account_suspended = user_signals.signal('user-account-suspended')
account_unsuspended = user_signals.signal('user-account-unsuspended')
account_deleted = user_signals.signal('user-account-deleted')
screen_name_changed = user_signals.signal('user-screen-name-changed')
