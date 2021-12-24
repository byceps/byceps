"""
byceps.blueprints.admin.news.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext
from wtforms import (
    DateField,
    FileField,
    RadioField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import InputRequired, Length, Optional, Regexp

from ....services.news.transfer.models import BodyFormat
from ....util.l10n import LocalizedForm


SLUG_REGEX = re.compile('^[a-z0-9-]+$')


class ChannelCreateForm(LocalizedForm):
    channel_id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )
    url_prefix = StringField(
        lazy_gettext('URL prefix'), [InputRequired(), Length(max=80)]
    )


class _ImageFormBase(LocalizedForm):
    alt_text = StringField(lazy_gettext('Alternative text'), [InputRequired()])
    caption = StringField(lazy_gettext('Caption'), [Optional()])
    attribution = StringField(lazy_gettext('Source'), [Optional()])


class ImageCreateForm(_ImageFormBase):
    image = FileField(lazy_gettext('Image file'), [InputRequired()])


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
                    'Lowercase letters, digits, and dash are allowed.'
                ),
            ),
        ],
    )
    title = StringField(
        lazy_gettext('Title'), [InputRequired(), Length(max=100)]
    )
    body_format = RadioField(
        lazy_gettext('Text format'),
        choices=[
            (BodyFormat.html.name, 'HTML'),
            (BodyFormat.markdown.name, 'Markdown'),
        ],
        coerce=lambda value: BodyFormat[value],
        validators=[InputRequired()],
    )
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])
    image_url_path = StringField(
        lazy_gettext('Image URL path'), [Optional(), Length(max=100)]
    )


class ItemUpdateForm(ItemCreateForm):
    pass


class ItemPublishLaterForm(LocalizedForm):
    publish_on = DateField(lazy_gettext('Date'), [InputRequired()])
    publish_at = TimeField(lazy_gettext('Time'), [InputRequired()])
