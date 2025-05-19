"""
byceps.services.site.navigation.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired

from byceps.services.language import language_service
from byceps.services.page import page_service
from byceps.services.site.models import SiteID
from byceps.services.site_navigation import site_navigation_service
from byceps.util.l10n import LocalizedForm


class _MenuBaseForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), validators=[InputRequired()])
    hidden = BooleanField(lazy_gettext('hidden'))


class MenuCreateForm(_MenuBaseForm):
    language_code = SelectField(
        lazy_gettext('Language code'), validators=[InputRequired()]
    )

    def set_language_choices(self):
        languages = language_service.get_languages()

        choices = [(language.code, language.code) for language in languages]
        choices.sort()
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.language_code.choices = choices


class SubMenuCreateForm(_MenuBaseForm):
    pass


class MenuUpdateForm(MenuCreateForm):
    pass


class _ItemBaseForm(LocalizedForm):
    label = StringField(lazy_gettext('Label'), validators=[InputRequired()])
    hidden = BooleanField(lazy_gettext('hidden'))


class ItemCreatePageForm(_ItemBaseForm):
    target_page_id = SelectField(
        lazy_gettext('Page'), validators=[InputRequired()]
    )

    def set_page_choices(self, site_id: SiteID):
        pages = page_service.get_pages_for_site(site_id)

        choices = [
            (str(page.id), f'{page.name} ({page.language_code})')
            for page in pages
        ]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.target_page_id.choices = choices


class ItemCreateUrlForm(_ItemBaseForm):
    target_url = StringField(lazy_gettext('URL'), validators=[InputRequired()])
    current_page_id = StringField(
        lazy_gettext('Current page ID'), validators=[InputRequired()]
    )


class ItemCreateViewForm(_ItemBaseForm):
    target_view_type = SelectField(
        lazy_gettext('View'), validators=[InputRequired()]
    )

    def set_view_type_choices(self):
        choices = [
            (view_type.name, view_type.label)
            for view_type in site_navigation_service.get_view_types()
        ]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.target_view_type.choices = choices


class ItemUpdateForm(_ItemBaseForm):
    target_type = SelectField(
        lazy_gettext('Target type'),
        [InputRequired()],
        choices=[
            ('page', lazy_gettext('Page')),
            ('endpoint', lazy_gettext('Endpoint')),
            ('view', lazy_gettext('View')),
            ('url', lazy_gettext('URL')),
        ],
    )
    target = StringField(lazy_gettext('Target'), validators=[InputRequired()])
    current_page_id = StringField(
        lazy_gettext('Current page ID'), validators=[InputRequired()]
    )
