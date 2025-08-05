"""
byceps.services.whereabouts.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


whereabouts_signals = Namespace()


whereabouts_client_registered = whereabouts_signals.signal(
    'whereabouts-client-registered'
)
whereabouts_client_approved = whereabouts_signals.signal(
    'whereabouts-client-approved'
)
whereabouts_client_deleted = whereabouts_signals.signal(
    'whereabouts-client-deleted'
)

whereabouts_client_signed_on = whereabouts_signals.signal(
    'whereabouts-client-signed-on'
)
whereabouts_client_signed_off = whereabouts_signals.signal(
    'whereabouts-client-signed-off'
)

whereabouts_status_updated = whereabouts_signals.signal(
    'whereabouts-status-updated'
)
