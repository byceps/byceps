"""
byceps.services.news.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext, pgettext
from wtforms import (
    BooleanField,
    DateField,
    FileField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import (
    InputRequired,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

from byceps.services.brand.models import BrandID
from byceps.services.news import news_item_service
from byceps.services.news.models import BodyFormat
from byceps.services.site import site_service
from byceps.util.l10n import LocalizedForm


SLUG_REGEX = re.compile('^[a-z0-9-]+$')


class _ChannelFormBase(LocalizedForm):
    announcement_site_id = SelectField(
        lazy_gettext('Site for announcement'), [Optional()]
    )

    def set_announcement_site_id_choices(self, brand_id: BrandID) -> None:
        sites = site_service.get_sites_for_brand(brand_id)

        choices = [
            (str(site.id), site.title)
            for site in sorted(sites, key=lambda site: site.title)
        ]
        choices.insert(0, ('', '<' + pgettext('site', 'none') + '>'))

        self.announcement_site_id.choices = choices


class ChannelCreateForm(_ChannelFormBase):
    channel_id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )


class ChannelUpdateForm(_ChannelFormBase):
    archived = BooleanField(lazy_gettext('archived'))


class _ImageFormBase(LocalizedForm):
    alt_text = StringField(lazy_gettext('Alternative text'), [InputRequired()])
    caption = StringField(lazy_gettext('Caption'), [Optional()])
    attribution = StringField(lazy_gettext('Source'), [Optional()])


class ImageCreateForm(_ImageFormBase):
    image = FileField(lazy_gettext('Image file'), [InputRequired()])


class ImageUpdateForm(_ImageFormBase):
    pass


class _ItemBaseForm(LocalizedForm):
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


class ItemCreateForm(_ItemBaseForm):
    def __init__(self, brand_id: BrandID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._brand_id = brand_id

    @staticmethod
    def validate_slug(form, field):
        slug = field.data.strip()

        if not news_item_service.is_slug_available(form._brand_id, slug):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )


class ItemUpdateForm(_ItemBaseForm):
    def __init__(self, brand_id: BrandID, current_slug: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._brand_id = brand_id
        self._current_slug = current_slug

    @staticmethod
    def validate_slug(form, field):
        slug = field.data.strip()

        if (
            slug != form._current_slug
            and not news_item_service.is_slug_available(form._brand_id, slug)
        ):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )


class ItemPublishLaterForm(LocalizedForm):
    publish_on = DateField(lazy_gettext('Date'), [InputRequired()])
    publish_at = TimeField(lazy_gettext('Time'), [InputRequired()])
