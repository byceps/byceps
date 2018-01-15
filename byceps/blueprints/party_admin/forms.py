"""
byceps.blueprints.party_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, DateTimeField, StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class UpdateForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
    starts_at = DateTimeField('Beginn', format='%d.%m.%Y %H:%M', validators=[InputRequired()])
    ends_at = DateTimeField('Ende', format='%d.%m.%Y %H:%M', validators=[InputRequired()])
    is_archived = BooleanField('archiviert')


class CreateForm(UpdateForm):
    id = StringField('ID', validators=[Length(min=1, max=40)])
