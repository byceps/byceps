"""
byceps.blueprints.admin.email.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Optional

from ....util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    config_id = StringField('ID')
    sender_address = StringField('Absender-Adresse', validators=[InputRequired()])
    sender_name = StringField('Absender-Name', validators=[Optional()])
    contact_address = StringField('Kontaktadresse', validators=[Optional()])
