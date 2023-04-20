"""
byceps.blueprints.admin.board.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, Length

from byceps.util.l10n import LocalizedForm


class BoardCreateForm(LocalizedForm):
    board_id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )


class CategoryCreateForm(LocalizedForm):
    slug = StringField(lazy_gettext('Slug'), [InputRequired(), Length(max=40)])
    title = StringField(
        lazy_gettext('Title'), [InputRequired(), Length(max=40)]
    )
    description = StringField(
        lazy_gettext('Text'), [InputRequired(), Length(max=80)]
    )


class CategoryUpdateForm(CategoryCreateForm):
    pass
