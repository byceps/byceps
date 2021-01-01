"""
byceps.blueprints.common.user.avatar.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import FileField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    image = FileField('Bilddatei', [InputRequired()])
