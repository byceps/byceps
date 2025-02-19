"""
byceps.blueprints.admin.brand.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from moneyed import CHF, DKK, EUR, GBP, NOK, SEK, USD
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.brand import brand_service
from byceps.services.brand.models import BrandID
from byceps.services.party import party_service
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )


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

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if brand_service.find_brand_by_title(title) is not None:
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
    current_party_id = SelectField(lazy_gettext('Current party'), [Optional()])
    archived = BooleanField(lazy_gettext('archived'))

    def __init__(self, current_title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_title = current_title

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if (
            title != form._current_title
            and brand_service.find_brand_by_title(title) is not None
        ):
            raise ValidationError(lazy_gettext('The value is already in use.'))

    def set_current_party_id_choices(self, brand_id: BrandID):
        parties = party_service.get_parties_for_brand(brand_id)
        parties.sort(key=lambda party: party.starts_at, reverse=True)

        choices = [(str(party.id), party.title) for party in parties]
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.current_party_id.choices = choices


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
