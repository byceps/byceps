"""
byceps.blueprints.admin.shop.order.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, RadioField, TextAreaField
from wtforms.validators import InputRequired, Length

from .....services.shop.order.transfer.models import PaymentMethod
from .....util.l10n import LocalizedForm


class CancelForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=800)])
    send_email = BooleanField('Auftraggeber/in per E-Mail über Stornierung informieren')


PAYMENT_METHOD_CHOICES = [
    (PaymentMethod.bank_transfer.name, 'Überweisung'),
    (PaymentMethod.cash.name, 'Barzahlung'),
    (PaymentMethod.direct_debit.name, 'Lastschrift'),
    (PaymentMethod.free.name, 'kostenlos'),
]


class MarkAsPaidForm(LocalizedForm):
    payment_method = RadioField('Zahlungsart',
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_CHOICES[0][0],
        validators=[InputRequired()])
