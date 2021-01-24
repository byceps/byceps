"""
byceps.blueprints.admin.shop.order.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import PaymentMethod
from .....util.l10n import LocalizedForm


class CancelForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Begründung'),
        validators=[InputRequired(), Length(max=1000)],
    )
    send_email = BooleanField(
        lazy_gettext('Auftraggeber/in per E-Mail über Stornierung informieren')
    )


def _get_payment_method_choices():
    return [
        (pm.name, order_service.find_payment_method_label(pm) or pm.name)
        for pm in PaymentMethod
    ]


class MarkAsPaidForm(LocalizedForm):
    payment_method = RadioField(
        lazy_gettext('Zahlungsart'),
        choices=_get_payment_method_choices(),
        default=PaymentMethod.bank_transfer.name,
        validators=[InputRequired()],
    )


class OrderNumberSequenceCreateForm(LocalizedForm):
    prefix = StringField(
        lazy_gettext('Statisches Präfix'), validators=[InputRequired()]
    )
