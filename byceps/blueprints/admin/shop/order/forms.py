"""
byceps.blueprints.admin.shop.order.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import PaymentMethod
from .....util.l10n import LocalizedForm


class CancelForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=1000)])
    send_email = BooleanField('Auftraggeber/in per E-Mail über Stornierung informieren')


def _get_payment_method_choices():
    return [
        (pm.name, order_service.find_payment_method_label(pm) or pm.name)
        for pm in PaymentMethod
    ]


class MarkAsPaidForm(LocalizedForm):
    payment_method = RadioField(
        'Zahlungsart',
        choices=_get_payment_method_choices(),
        default=PaymentMethod.bank_transfer.name,
        validators=[InputRequired()],
    )


class OrderNumberSequenceCreateForm(LocalizedForm):
    prefix = StringField('Statisches Präfix', validators=[InputRequired()])
