"""
byceps.services.page.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from flask_babel import gettext, lazy_gettext
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Optional, ValidationError

from byceps.services.language import language_service
from byceps.services.page.models import Page
from byceps.services.site.models import SiteID
from byceps.services.site_navigation import site_navigation_service
from byceps.util.forms import MultiCheckboxField
from byceps.util.l10n import LocalizedForm


class CopyPagesForm(LocalizedForm):
    source_page_ids = MultiCheckboxField(
        lazy_gettext('Pages'), validators=[Optional()]
    )

    def set_source_page_id_choices(self, pages: Sequence[Page]):
        pages = list(pages)
        pages.sort(key=lambda page: (page.name, page.language_code))

        choices = [
            (str(page.id), f'{page.name} ({page.language_code})')
            for page in pages
        ]
        self.source_page_ids.choices = choices


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
