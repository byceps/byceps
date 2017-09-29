"""
byceps.blueprints.user_badge_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    brand_id = SelectField('Marke')
    slug = StringField('Slug', validators=[InputRequired(), Length(max=40)])
    label = StringField('Bezeichnung', validators=[InputRequired(), Length(max=80)])
    description = TextAreaField('Beschreibung')
    image_filename = StringField('Bilddateiname', validators=[InputRequired(), Length(max=80)])
    featured = BooleanField('featured')

    def set_brand_choices(self, brands):
        choices = [(brand.id, brand.title) for brand in brands]
        choices.insert(0, ('', '<keine>'))
        self.brand_id.choices = choices
