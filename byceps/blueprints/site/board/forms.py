"""
byceps.blueprints.site.board.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from ....util.l10n import LocalizedForm


class PostingCreateForm(LocalizedForm):
    body = TextAreaField(lazy_gettext('Text'), validators=[InputRequired()])


class PostingUpdateForm(PostingCreateForm):
    pass


class TopicCreateForm(PostingCreateForm):
    title = StringField(
        lazy_gettext('Title'), validators=[InputRequired(), Length(max=80)]
    )


class TopicUpdateForm(TopicCreateForm):
    pass
