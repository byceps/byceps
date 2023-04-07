"""
byceps.blueprints.admin.shop.shop.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from moneyed import CHF, DKK, EUR, GBP, NOK, SEK, USD
from wtforms import SelectField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    currency = SelectField(lazy_gettext('Currency'), [InputRequired()])

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
