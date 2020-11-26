"""
byceps.blueprints.admin.email.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from ....services.brand import service as brand_service
from ....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    sender_address = StringField('Absender-Adresse', validators=[InputRequired()])
    sender_name = StringField('Absender-Name', validators=[Optional()])
    contact_address = StringField('Kontaktadresse', validators=[Optional()])

    def set_brand_choices(self):
        brands = brand_service.get_all_brands()
        brands.sort(key=lambda brand: brand.title)
        self.brand_id.choices = [(brand.id, brand.title) for brand in brands]


class CreateForm(_BaseForm):
    config_id = StringField('ID', validators=[InputRequired()])
    brand_id = SelectField('Marke', validators=[InputRequired()])


class UpdateForm(_BaseForm):
    config_id = StringField('ID')
