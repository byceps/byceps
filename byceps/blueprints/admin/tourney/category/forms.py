"""
byceps.blueprints.admin.tourney.category.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Length

from .....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField('Titel', [InputRequired(), Length(max=40)])


class UpdateForm(CreateForm):
    pass
