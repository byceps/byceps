"""
byceps.blueprints.admin.shop.shop.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length

from .....services.brand import service as brand_service
from .....services.email import service as email_service
from .....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
    email_config_id = SelectField('E-Mail-Konfiguration', validators=[InputRequired()])

    def set_brand_choices(self):
        brands = brand_service.get_all_brands()
        brands.sort(key=lambda brand: brand.title)
        self.brand_id.choices = [(brand.id, brand.title) for brand in brands]

    def set_email_config_choices(self):
        configs = email_service.get_all_configs()
        configs.sort(key=lambda config: config.id)
        self.email_config_id.choices = [(c.id, c.id) for c in configs]


class CreateForm(_BaseForm):
    id = StringField('ID', validators=[InputRequired()])
    brand_id = SelectField('Marke', validators=[InputRequired()])


class UpdateForm(_BaseForm):
    pass
