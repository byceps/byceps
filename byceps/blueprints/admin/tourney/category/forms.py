"""
byceps.blueprints.admin.tourney.category.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, Length

from byceps.util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'), [InputRequired(), Length(max=40)]
    )


class UpdateForm(CreateForm):
    pass
