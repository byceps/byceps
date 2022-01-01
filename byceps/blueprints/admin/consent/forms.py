"""
byceps.blueprints.admin.consent.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, Length

from ....util.l10n import LocalizedForm


class SubjectCreateForm(LocalizedForm):
    subject_name = StringField(
        lazy_gettext('Internal name'), [InputRequired(), Length(max=40)]
    )
    subject_title = StringField(
        lazy_gettext('Internal title'), [InputRequired(), Length(max=40)]
    )
    checkbox_label = StringField(
        lazy_gettext('Checkbox label'), [InputRequired(), Length(max=200)]
    )
    checkbox_link_target = StringField(
        lazy_gettext('Checkbox label link target'),
        [InputRequired(), Length(max=200)],
    )
