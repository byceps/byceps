"""
byceps.blueprints.brand_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import Length

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    id = StringField('ID', validators=[Length(min=1, max=20)])
    title = StringField('Titel', validators=[Length(min=1, max=40)])
