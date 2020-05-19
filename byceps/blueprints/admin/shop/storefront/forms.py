"""
byceps.blueprints.admin.shop.storefront.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    catalog_id = SelectField('Katalog')
    order_number_sequence_id = SelectField('Bestellnummer-Sequenz')

    def set_catalog_choices(self, catalogs):
        catalogs.sort(key=lambda catalog: catalog.title)

        choices = [(str(catalog.id), catalog.title) for catalog in catalogs]
        choices.insert(0, ('', '<keiner>'))
        self.catalog_id.choices = choices

    def set_order_number_sequence_choices(self, sequences):
        sequences.sort(key=lambda seq: seq.prefix)

        choices = [(str(seq.id), seq.prefix) for seq in sequences]
        choices.insert(0, ('', '<keine>'))
        self.order_number_sequence_id.choices = choices


class StorefrontCreateForm(_BaseForm):
    id = StringField('ID', validators=[InputRequired()])


class StorefrontUpdateForm(_BaseForm):
    closed = BooleanField('geschlossen')
