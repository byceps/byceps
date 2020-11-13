"""
byceps.blueprints.admin.board.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Length

from ....util.l10n import LocalizedForm


class BoardCreateForm(LocalizedForm):
    board_id = StringField('ID', validators=[Length(min=1, max=40)])


class CategoryCreateForm(LocalizedForm):
    slug = StringField('Slug', [InputRequired(), Length(max=40)])
    title = StringField('Titel', [InputRequired(), Length(max=40)])
    description = StringField('Text', [InputRequired(), Length(max=80)])


class CategoryUpdateForm(CategoryCreateForm):
    pass
