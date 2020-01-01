"""
byceps.blueprints.admin.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm

from ....services.email import service as email_service
from ....services.party import service as party_service


class _BaseForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
    server_name = StringField('Servername', validators=[InputRequired()])
    email_config_id = SelectField('E-Mail-Konfiguration', validators=[InputRequired()])
    party_id = SelectField('Party-ID', validators=[Optional()])
    enabled = BooleanField('aktiv')
    user_account_creation_enabled  = BooleanField('Benutzerregistrierung geöffnet')
    login_enabled = BooleanField('Benutzeranmeldung geöffnet')

    def set_email_config_choices(self):
        configs = email_service.get_all_configs()
        configs.sort(key=lambda config: config.id)
        self.email_config_id.choices = [(c.id, c.id) for c in configs]

    def set_party_choices(self):
        parties = party_service.get_all_parties()
        parties.sort(key=lambda party: party.id)

        choices = [(str(p.id), p.title) for p in parties]
        choices.insert(0, ('', '<keine>'))
        self.party_id.choices = choices


class CreateForm(_BaseForm):
    id = StringField('ID', validators=[Length(min=1, max=40)])


class UpdateForm(_BaseForm):
    archived = BooleanField('archiviert')
