"""
byceps.blueprints.board_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class CategoryCreateForm(LocalizedForm):
    slug = StringField('Slug', [InputRequired(), Length(max=40)])
    title = StringField('Titel', [InputRequired(), Length(max=40)])
    description = StringField('Text', [InputRequired(), Length(max=80)])


class CategoryUpdateForm(CategoryCreateForm):
    pass
