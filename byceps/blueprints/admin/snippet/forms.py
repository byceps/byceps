"""
byceps.blueprints.admin.snippet.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])


class UpdateForm(CreateForm):
    pass
