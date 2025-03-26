"""
byceps.services.shop.storefront.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext, pgettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    catalog_id = SelectField(lazy_gettext('Catalog'))
    order_number_sequence_id = SelectField(
        lazy_gettext('Order number sequence'), validators=[InputRequired()]
    )

    def set_catalog_choices(self, catalogs):
        catalogs.sort(key=lambda catalog: catalog.title)

        choices = [(str(catalog.id), catalog.title) for catalog in catalogs]
        choices.insert(0, ('', '<' + pgettext('catalog', 'none') + '>'))
        self.catalog_id.choices = choices

    def set_order_number_sequence_choices(self, sequences):
        sequences.sort(key=lambda seq: seq.prefix)

        choices = [(str(seq.id), seq.prefix) for seq in sequences]
        choices.insert(0, ('', '<' + pgettext('sequence', 'none') + '>'))
        self.order_number_sequence_id.choices = choices


class StorefrontCreateForm(_BaseForm):
    id = StringField(lazy_gettext('ID'), validators=[InputRequired()])


class StorefrontUpdateForm(_BaseForm):
    closed = BooleanField(lazy_gettext('closed'))
