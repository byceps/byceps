"""
byceps.blueprints.admin.site.navigation.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired

from .....services.page import page_service
from .....services.site.models import SiteID
from .....services.site_navigation import site_navigation_service
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
    label = StringField(lazy_gettext('Label'), validators=[InputRequired()])
    hidden = BooleanField(lazy_gettext('hidden'))


class ItemCreateEndpointForm(_ItemBaseForm):
    target_endpoint = SelectField(
        lazy_gettext('Endpoint'),
        choices=[
            ('', '<' + lazy_gettext('choose') + '>'),
            ('news.index', lazy_gettext('News')),
            ('seating.index', lazy_gettext('Seating plan')),
            ('attendance.attendees', lazy_gettext('Attendees')),
            ('shop_order.order_form', lazy_gettext('Shop')),
            ('board.category_index', lazy_gettext('Board')),
            ('orga_team.index', lazy_gettext('Orga team')),
        ],
        validators=[InputRequired()],
    )
    current_page_id = StringField(
        lazy_gettext('Current page ID'), validators=[InputRequired()]
    )


class ItemCreatePageForm(_ItemBaseForm):
    target_page_id = SelectField(
        lazy_gettext('Page'), validators=[InputRequired()]
    )

    def set_page_choices(self, site_id: SiteID, language_code: str):
        page_ids_and_names = page_service.get_page_ids_and_names(
            site_id, language_code
        )

        choices = [(str(page_id), name) for page_id, name in page_ids_and_names]
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
