"""
byceps.blueprints.news_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import re

from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, Regexp

from ...util.l10n import LocalizedForm


SLUG_REGEX = re.compile('^[a-z0-9-]+$')


class ItemCreateForm(LocalizedForm):
    slug = StringField('Slug', [InputRequired(), Length(max=80), Regexp(SLUG_REGEX, message='Nur Kleinbuchstaben, Ziffern und Bindestrich sind erlaubt.')])
    title = StringField('Titel', [InputRequired(), Length(max=80)])
    body = TextAreaField('Text', [InputRequired()])
    image_url_path = StringField('Bild-URL-Pfad', [Optional(), Length(max=80)])


class ItemUpdateForm(ItemCreateForm):
    pass
