"""
byceps.blueprints.site.user_group.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

from byceps.util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'), [InputRequired(), Length(max=40)]
    )
    description = TextAreaField(
        lazy_gettext('Description'), [Optional(), Length(max=200)]
    )


class UpdateForm(CreateForm):
    pass
