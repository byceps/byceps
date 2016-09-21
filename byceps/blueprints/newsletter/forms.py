# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import RadioField
from wtforms.validators import DataRequired

from ...services.newsletter.types import SubscriptionState
from ...util.l10n import LocalizedForm


class SubscriptionForm(LocalizedForm):
    state = RadioField(
        'Abonnement',
        choices=[
            (SubscriptionState.requested.name, 'ja, bitte'),
            (SubscriptionState.declined.name, 'nein, danke'),
        ],
        validators=[DataRequired()])
