# -*- coding: utf-8 -*-

"""
byceps.services.newsletter.types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


SubscriptionState = Enum('SubscriptionState', ['requested', 'declined'])
