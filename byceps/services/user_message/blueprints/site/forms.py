"""
byceps.services.user_message.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length

from byceps.util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    body = TextAreaField(
        lazy_gettext('Text'), validators=[InputRequired(), Length(max=2000)]
    )
