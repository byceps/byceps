"""
byceps.blueprints.site.board.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length

from ....util.l10n import LocalizedForm


class PostingCreateForm(LocalizedForm):
    body = TextAreaField('Text', validators=[InputRequired()])


class PostingUpdateForm(PostingCreateForm):
    pass


class TopicCreateForm(PostingCreateForm):
    title = StringField('Titel', validators=[InputRequired(), Length(max=80)])


class TopicUpdateForm(TopicCreateForm):
    pass
