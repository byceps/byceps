"""
byceps.blueprints.admin.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm

from ....services.email import service as email_service


class UpdateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=20)])
    server_name = StringField('Servername', validators=[InputRequired()])
    email_config_id = SelectField('E-Mail-Konfiguration', validators=[InputRequired()])
    party_id = StringField('Party-ID', validators=[Optional()])

    def set_email_config_choices(self):
        configs = email_service.get_all_configs()
        configs.sort(key=lambda config: config.id)
        self.email_config_id.choices = [(c.id, c.id) for c in configs]


class CreateForm(UpdateForm):
    id = StringField('ID', validators=[Length(min=1, max=40)])
