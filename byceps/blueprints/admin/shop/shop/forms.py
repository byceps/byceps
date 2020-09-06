"""
byceps.blueprints.admin.shop.shop.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length

from .....services.email import service as email_service
from .....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
    email_config_id = SelectField('E-Mail-Konfiguration', validators=[InputRequired()])

    def set_email_config_choices(self):
        configs = email_service.get_all_configs()
        configs.sort(key=lambda config: config.id)
        self.email_config_id.choices = [(c.id, c.id) for c in configs]


class CreateForm(_BaseForm):
    id = StringField('ID', validators=[InputRequired()])


class UpdateForm(_BaseForm):
    pass
