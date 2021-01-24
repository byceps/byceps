"""
byceps.blueprints.admin.news.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext
from wtforms import FileField, StringField, TextAreaField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, Length, Optional, Regexp

from ....util.l10n import LocalizedForm


SLUG_REGEX = re.compile('^[a-z0-9-]+$')


class ChannelCreateForm(LocalizedForm):
    channel_id = StringField(
        lazy_gettext('ID'), validators=[Length(min=1, max=40)]
    )
    url_prefix = StringField(
        lazy_gettext('URL-Präfix'), [InputRequired(), Length(max=80)]
    )


class _ImageFormBase(LocalizedForm):
    alt_text = StringField(lazy_gettext('Alternativtext'), [InputRequired()])
    caption = StringField(lazy_gettext('Bildunterschrift'), [Optional()])
    attribution = StringField(lazy_gettext('Bildquelle'), [Optional()])


class ImageCreateForm(_ImageFormBase):
    image = FileField(lazy_gettext('Bilddatei'), [InputRequired()])


class ImageUpdateForm(_ImageFormBase):
    pass


class ItemCreateForm(LocalizedForm):
    slug = StringField(
        lazy_gettext('Slug'),
        [
            InputRequired(),
            Length(max=100),
            Regexp(
                SLUG_REGEX,
                message=lazy_gettext(
                    'Nur Kleinbuchstaben, Ziffern und Bindestrich sind erlaubt.'
                ),
            ),
        ],
    )
    title = StringField(
        lazy_gettext('Titel'), [InputRequired(), Length(max=100)]
    )
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])
    image_url_path = StringField(
        lazy_gettext('Bild-URL-Pfad'), [Optional(), Length(max=100)]
    )


class ItemUpdateForm(ItemCreateForm):
    pass


class ItemPublishLaterForm(LocalizedForm):
    publish_on = DateField(lazy_gettext('Datum'), [InputRequired()])
    publish_at = TimeField(lazy_gettext('Uhrzeit'), [InputRequired()])
