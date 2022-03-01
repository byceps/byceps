"""
byceps.blueprints.site.user_group.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Optional

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField(lazy_gettext('Title'), [InputRequired()])
    description = TextAreaField(lazy_gettext('Description'), [Optional()])
