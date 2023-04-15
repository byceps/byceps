"""
byceps.blueprints.site.shop.orders.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext
from schwifty import IBAN
from schwifty.exceptions import SchwiftyException
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import (
    InputRequired,
    Length,
    NumberRange,
    ValidationError,
)

from .....services.shop.order.models.order import Order
from .....util.l10n import LocalizedForm


class CancelForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(min=10, max=1000)],
    )


class _RequestRefundFormBase(LocalizedForm):
    recipient_name = StringField(
        'Kontoinhaber', validators=[InputRequired(), Length(min=2, max=80)]
    )
    recipient_iban = StringField('IBAN', validators=[InputRequired()])

    @staticmethod
    def filter_recipient_name(data):
        return data.strip() if data is not None else None

    @staticmethod
    def filter_recipient_iban(data):
        return re.sub(r'\s', '', data).upper() if data is not None else None

    @staticmethod
    def validate_recipient_iban(form, field):
        try:
            IBAN(field.data)  # Validate, but ignore the resulting object.
        except SchwiftyException:
            raise ValidationError('Ungültige IBAN')


class RequestFullRefundForm(_RequestRefundFormBase):
    pass


class RequestPartialRefundForm(_RequestRefundFormBase):
    amount_donation = IntegerField(
        'Spende (in Euro)', validators=[InputRequired(), NumberRange(min=0)]
    )

    def __init__(self, order: Order, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.order = order

    @staticmethod
    def validate_amount_donation(form, field):
        amount = field.data
        if amount is None:
            return

        if field.data > form.order.total_amount.amount:
            raise ValidationError(
                'Der Spendenbetrag darf den Bestellbetrag nicht übersteigen.'
            )
