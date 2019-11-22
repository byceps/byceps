"""
byceps.blueprints.user.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


user_signals = Namespace()


email_address_changed = user_signals.signal('email-address-changed')
email_address_confirmed = user_signals.signal('email-address-confirmed')
account_created = user_signals.signal('user-account-created')
account_suspended = user_signals.signal('user-account-suspended')
account_unsuspended = user_signals.signal('user-account-unsuspended')
account_deleted = user_signals.signal('user-account-deleted')
screen_name_changed = user_signals.signal('user-screen-name-changed')
