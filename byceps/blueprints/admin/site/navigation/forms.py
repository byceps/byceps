"""
byceps.blueprints.admin.site.navigation.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), validators=[InputRequired()])
    language_code = StringField(
        lazy_gettext('Language code'), validators=[InputRequired()]
    )
    hidden = BooleanField(lazy_gettext('hidden'))


class MenuCreateForm(_BaseForm):
    pass
