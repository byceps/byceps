"""
byceps.blueprints.site.guest_server.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import Optional

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    hostname = StringField(lazy_gettext('Hostname'), validators=[Optional()])
    notes = TextAreaField(lazy_gettext('Notes'), validators=[Optional()])
