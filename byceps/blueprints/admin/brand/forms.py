"""
byceps.blueprints.admin.brand.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from moneyed import CHF, DKK, EUR, GBP, NOK, SEK, USD
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.brand import brand_service
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )

    @staticmethod
    def validate_title(form, field):
        title = field.data
        if brand_service.find_brand_by_title(title) is not None:
            raise ValidationError(lazy_gettext('The value is already in use.'))


class CreateForm(_BaseForm):
    id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=20)]
    )
    currency = SelectField(lazy_gettext('Currency'), [InputRequired()])

    @staticmethod
    def validate_id(form, field):
        brand_id = field.data
        if brand_service.find_brand(brand_id) is not None:
            raise ValidationError(lazy_gettext('The value is already in use.'))

    def set_currency_choices(self, locale: str):
        currencies = [CHF, DKK, EUR, GBP, NOK, SEK, USD]

        def get_label(currency) -> str:
            name = currency.get_name(locale)
            return f'{name} ({currency.code})'

        choices = [
            (currency.code, get_label(currency)) for currency in currencies
        ]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.currency.choices = choices


class UpdateForm(_BaseForm):
    image_filename = StringField(
        lazy_gettext('Image filename'), validators=[Optional()]
    )
    archived = BooleanField(lazy_gettext('archived'))


class EmailConfigUpdateForm(LocalizedForm):
    sender_address = StringField(
        lazy_gettext('Sender address'), validators=[InputRequired()]
    )
    sender_name = StringField(
        lazy_gettext('Sender name'), validators=[Optional()]
    )
    contact_address = StringField(
        lazy_gettext('Contact address'), validators=[Optional()]
    )
