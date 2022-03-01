"""
byceps.blueprints.site.user.avatar.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import FileField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    image = FileField(lazy_gettext('Image file'), [InputRequired()])
