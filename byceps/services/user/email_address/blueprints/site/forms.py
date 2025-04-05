"""
byceps.services.user.email_address.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class RequestConfirmationEmailForm(LocalizedForm):
    screen_name = StringField(lazy_gettext('Username'), [InputRequired()])
