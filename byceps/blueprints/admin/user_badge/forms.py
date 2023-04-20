"""
byceps.blueprints.admin.user_badge.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext
from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp

from byceps.util.l10n import LocalizedForm


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
                    'Lowercase letters, digits, and dash are allowed.'
                ),
            ),
        ],
    )
    label = StringField(
        lazy_gettext('Label'), [InputRequired(), Length(max=80)]
    )
    description = TextAreaField(lazy_gettext('Description'))
    image_filename = StringField(
        lazy_gettext('Image filename'), [InputRequired(), Length(max=80)]
    )
    brand_id = SelectField(lazy_gettext('Brand'))
    featured = BooleanField(lazy_gettext('featured'))

    def set_brand_choices(self, brands):
        choices = [(brand.id, brand.title) for brand in brands]
        choices.insert(0, ('', lazy_gettext('<no restriction>')))
        self.brand_id.choices = choices


class UpdateForm(CreateForm):
    pass


class AwardForm(LocalizedForm):
    badge_id = SelectField(lazy_gettext('Badge'), [InputRequired()])

    def set_badge_choices(self, badges):
        choices = [(str(badge.id), badge.label) for badge in badges]
        choices.sort(key=lambda choice: choice[1])
        self.badge_id.choices = choices
