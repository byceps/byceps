"""
byceps.services.newsletter.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


newsletter_signals = Namespace()


newsletter_subscribed = newsletter_signals.signal('newsletter-subscribed')
newsletter_unsubscribed = newsletter_signals.signal('newsletter-unsubscribed')
