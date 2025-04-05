"""
byceps.services.user.avatar.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import FileField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    image = FileField(lazy_gettext('Image file'), [InputRequired()])
