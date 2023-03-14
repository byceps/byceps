"""
byceps.blueprints.admin.page.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext, lazy_gettext
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, ValidationError

from ....services.language import language_service
from ....services.site.models import SiteID
from ....services.site_navigation import site_navigation_service
from ....util.l10n import LocalizedForm


class _PageBaseForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    language_code = SelectField(
        lazy_gettext('Language code'), [InputRequired()]
    )
    url_path = StringField(lazy_gettext('URL path'), [InputRequired()])

    title = StringField(lazy_gettext('Title'), [InputRequired()])
    head = TextAreaField(lazy_gettext('Header'))
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])

    def set_language_code_choices(self):
        languages = language_service.get_languages()
        choices = [(language.code, language.code) for language in languages]
        choices.sort()
        self.language_code.choices = choices

    @staticmethod
    def validate_url_path(form, field):
        if not field.data.startswith('/'):
            raise ValidationError(
                gettext('URL path must begin with a forward slash.')
            )


class CreateForm(_PageBaseForm):
    pass


class UpdateForm(_PageBaseForm):
    pass


class SetNavMenuForm(LocalizedForm):
    nav_menu_id = SelectField(lazy_gettext('Navigation menu'))

    def set_nav_menu_choices(self, site_id: SiteID):
        menus = site_navigation_service.get_menus(site_id)
        choices = [
            (str(menu.id), f'{menu.name} ({menu.language_code})')
            for menu in menus
        ]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('none') + '>'))
        self.nav_menu_id.choices = choices
