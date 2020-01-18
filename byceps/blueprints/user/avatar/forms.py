"""
byceps.blueprints.user.avatar.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import FileField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    image = FileField('Bilddatei', [InputRequired()])
