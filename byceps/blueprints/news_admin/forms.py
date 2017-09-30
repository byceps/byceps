"""
byceps.blueprints.news_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

from ...util.l10n import LocalizedForm


class ItemCreateForm(LocalizedForm):
    slug = StringField('Slug', [InputRequired(), Length(max=80)])
    title = StringField('Titel', [InputRequired(), Length(max=80)])
    body = TextAreaField('Text', [InputRequired(), Length(max=80)])
    image_url_path = StringField('Bild-URL-Pfad', [Optional(), Length(max=80)])


class ItemUpdateForm(ItemCreateForm):
    pass
