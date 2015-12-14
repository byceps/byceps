# -*- coding: utf-8 -*-

"""
byceps.blueprints.party_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from wtforms import DateTimeField, IntegerField, SelectField, StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    id = StringField('ID', validators=[Length(min=1, max=40)])
    brand_id = SelectField('Marke')
    title = StringField('Titel', validators=[Length(min=1, max=40)])
    starts_at = DateTimeField('Beginn', format='%d.%m.%Y %H:%M', validators=[InputRequired()])
    ends_at = DateTimeField('Ende', format='%d.%m.%Y %H:%M', validators=[InputRequired()])

    def set_brand_choices(self, brands):
        choices = list(map(attrgetter('id', 'title'), brands))
        self.brand_id.choices = choices
