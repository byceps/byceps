"""
byceps.blueprints.admin.user_badge.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext
from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp

from ....util.l10n import LocalizedForm


SLUG_REGEX = re.compile('^[a-z0-9-]+$')


class CreateForm(LocalizedForm):
    slug = StringField(
        lazy_gettext('Slug'),
        [
            InputRequired(),
            Length(max=80),
            Regexp(
                SLUG_REGEX,
                message=lazy_gettext(
                    'Nur Kleinbuchstaben, Ziffern und Bindestrich sind erlaubt.'
                ),
            ),
        ],
    )
    label = StringField(
        lazy_gettext('Bezeichnung'), [InputRequired(), Length(max=80)]
    )
    description = TextAreaField(lazy_gettext('Beschreibung'))
    image_filename = StringField(
        lazy_gettext('Bilddateiname'), [InputRequired(), Length(max=80)]
    )
    brand_id = SelectField(lazy_gettext('Marke'))
    featured = BooleanField(lazy_gettext('featured'))

    def set_brand_choices(self, brands):
        choices = [(brand.id, brand.title) for brand in brands]
        choices.insert(0, ('', lazy_gettext('<keine Einschränkung>')))
        self.brand_id.choices = choices


class UpdateForm(CreateForm):
    pass


class AwardForm(LocalizedForm):
    badge_id = SelectField(lazy_gettext('Badge'), [InputRequired()])

    def set_badge_choices(self, badges):
        choices = [(str(badge.id), badge.label) for badge in badges]
        choices.sort(key=lambda choice: choice[1])
        self.badge_id.choices = choices
