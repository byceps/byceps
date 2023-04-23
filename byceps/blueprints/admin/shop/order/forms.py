"""
byceps.blueprints.admin.shop.order.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from byceps.services.shop.order import order_service
from byceps.services.shop.order.models.payment import DEFAULT_PAYMENT_METHODS
from byceps.services.shop.payment import payment_gateway_service
from byceps.util.l10n import LocalizedForm


class AddNoteForm(LocalizedForm):
    text = TextAreaField(lazy_gettext('Text'), validators=[InputRequired()])


class CancelForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )
    send_email = BooleanField(
        lazy_gettext('Actively inform orderer via email of cancelation')
    )


class MarkAsPaidForm(LocalizedForm):
    payment_method = RadioField(
        lazy_gettext('Payment type'),
        default='bank_transfer',
        validators=[InputRequired()],
    )

    def set_payment_method_choices(self):
        default_payment_methods = [
            (pm, order_service.find_payment_method_label(pm) or pm)
            for pm in DEFAULT_PAYMENT_METHODS
        ]
        payment_gateway_methods = [
            (payment_gateway.id, payment_gateway.name)
            for payment_gateway in payment_gateway_service.get_enabled_payment_gateways()
        ]

        choices = default_payment_methods + payment_gateway_methods
        choices.sort()
        self.payment_method.choices = choices


class OrderNumberSequenceCreateForm(LocalizedForm):
    prefix = StringField(
        lazy_gettext('Static prefix'), validators=[InputRequired()]
    )
