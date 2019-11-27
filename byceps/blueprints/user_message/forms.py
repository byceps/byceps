"""
byceps.blueprints.user_message.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    body = TextAreaField('Text', validators=[InputRequired(), Length(max=2000)])
