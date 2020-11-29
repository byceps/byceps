"""
byceps.blueprints.admin.shop.shop.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length

from .....services.brand import service as brand_service
from .....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    id = StringField('ID', validators=[InputRequired()])
    brand_id = SelectField('Marke', validators=[InputRequired()])
    title = StringField('Titel', validators=[Length(min=1, max=40)])

    def set_brand_choices(self):
        brands = brand_service.get_all_brands()
        brands.sort(key=lambda brand: brand.title)
        self.brand_id.choices = [(brand.id, brand.title) for brand in brands]
