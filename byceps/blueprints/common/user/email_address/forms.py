"""
byceps.blueprints.common.user.email_address.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class RequestConfirmationEmailForm(LocalizedForm):
    screen_name = StringField('Benutzername', [InputRequired()])
