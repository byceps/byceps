"""
byceps.blueprints.api.v1.tourney.avatar.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import FileField, StringField
from wtforms.validators import InputRequired

from ......util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    party_id = StringField(lazy_gettext('Party ID'), [InputRequired()])
    creator_id = StringField(lazy_gettext('User ID'), [InputRequired()])
    image = FileField(lazy_gettext('Image file'), [InputRequired()])
