"""
byceps.services.shop.shop.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import SelectField
from wtforms.validators import InputRequired

from byceps.services.currency import currency_service
from byceps.util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    currency = SelectField(lazy_gettext('Currency'), [InputRequired()])

    def set_currency_choices(self, locale: str):
        def get_label(currency) -> str:
            name = currency.get_name(locale)
            return f'{name} ({currency.code})'

        choices = [
            (currency.code, get_label(currency))
            for currency in currency_service.get_currencies()
        ]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.currency.choices = choices
