"""
byceps.blueprints.admin.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=20)])
    server_name = StringField('Servername', validators=[InputRequired()])
    email_config_id = StringField('E-Mail-Konfiguration', validators=[InputRequired()])
    party_id = StringField('Party-ID', validators=[Optional()])

class CreateForm(UpdateForm):
    id = StringField('ID', validators=[Length(min=1, max=40)])
