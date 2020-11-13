"""
byceps.blueprints.admin.email.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    sender_address = StringField('Absender-Adresse', validators=[InputRequired()])
    sender_name = StringField('Absender-Name', validators=[Optional()])
    contact_address = StringField('Kontaktadresse', validators=[Optional()])


class CreateForm(_BaseForm):
    config_id = StringField('ID', validators=[InputRequired()])


class UpdateForm(_BaseForm):
    config_id = StringField('ID')
