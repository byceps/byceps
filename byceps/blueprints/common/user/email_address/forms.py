"""
byceps.blueprints.common.user.email_address.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class RequestConfirmationEmailForm(LocalizedForm):
    screen_name = StringField('Benutzername', [InputRequired()])
