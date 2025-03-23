"""
byceps.services.board.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, Length, ValidationError

from byceps.services.board import board_service
from byceps.util.l10n import LocalizedForm


class BoardCreateForm(LocalizedForm):
    board_id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )

    @staticmethod
    def validate_board_id(form, field):
        board_id = field.data.strip()

        if board_service.find_board(board_id):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
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
