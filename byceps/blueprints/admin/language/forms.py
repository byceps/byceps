"""
byceps.blueprints.admin.language.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    code = StringField(lazy_gettext('Language code'), [InputRequired()])
