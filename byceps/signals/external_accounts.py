"""
byceps.signals.external_accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


external_accounts_signals = Namespace()


external_account_connected = external_accounts_signals.signal(
    'external-account-connected'
)
external_account_disconnected = external_accounts_signals.signal(
    'external-account-disconnected'
)
