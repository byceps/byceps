"""
byceps.blueprints.api.v1.tourney.avatar.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import FileField, StringField
from wtforms.validators import InputRequired

from ......util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    party_id = StringField('Party-ID', [InputRequired()])
    creator_id = StringField('User-ID', [InputRequired()])
    image = FileField('Bilddatei', [InputRequired()])
