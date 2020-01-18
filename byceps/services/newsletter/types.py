"""
byceps.services.newsletter.types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


SubscriptionState = Enum('SubscriptionState', ['requested', 'declined'])
