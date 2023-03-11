"""
byceps.blueprints.admin.site.navigation.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class _MenuBaseForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), validators=[InputRequired()])
    language_code = StringField(
        lazy_gettext('Language code'), validators=[InputRequired()]
    )
    hidden = BooleanField(lazy_gettext('hidden'))


class MenuCreateForm(_MenuBaseForm):
    pass


class MenuUpdateForm(_MenuBaseForm):
    pass


class _ItemBaseForm(LocalizedForm):
    target_type = SelectField(
        lazy_gettext('Target type'),
        [InputRequired()],
        choices=[
            ('', '<' + lazy_gettext('choose') + '>'),
            ('page', lazy_gettext('page')),
            ('endpoint', lazy_gettext('endpoint')),
            ('url', lazy_gettext('URL')),
        ],
    )
    target = StringField(lazy_gettext('Target'), validators=[InputRequired()])
    label = StringField(lazy_gettext('Label'), validators=[InputRequired()])
    current_page_id = StringField(
        lazy_gettext('Current page ID'), validators=[InputRequired()]
    )
    hidden = BooleanField(lazy_gettext('hidden'))


class ItemCreateForm(_ItemBaseForm):
    pass


class ItemUpdateForm(_ItemBaseForm):
    pass
