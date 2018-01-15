"""
byceps.blueprints.tourney.avatar.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import FileField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    image = FileField('Bilddatei', [InputRequired()])
