"""
byceps.blueprints.user_badge_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import re

from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp

from ...util.l10n import LocalizedForm


SLUG_REGEX = re.compile('^[a-z0-9-]+$')


class CreateForm(LocalizedForm):
    brand_id = SelectField('Marke')
    slug = StringField('Slug', [InputRequired(), Length(max=80), Regexp(SLUG_REGEX, message='Nur Kleinbuchstaben, Ziffern und Bindestrich sind erlaubt.')])
    label = StringField('Bezeichnung', [InputRequired(), Length(max=80)])
    description = TextAreaField('Beschreibung')
    image_filename = StringField('Bilddateiname', [InputRequired(), Length(max=80)])
    featured = BooleanField('featured')

    def set_brand_choices(self, brands):
        choices = [(brand.id, brand.title) for brand in brands]
        choices.insert(0, ('', '<keine>'))
        self.brand_id.choices = choices
