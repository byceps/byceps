"""
byceps.blueprints.site.user_message.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    body = TextAreaField('Text', validators=[InputRequired(), Length(max=2000)])
