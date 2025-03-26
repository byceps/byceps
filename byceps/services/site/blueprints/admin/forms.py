"""
byceps.services.site.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext, pgettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.board import board_service
from byceps.services.news import news_channel_service
from byceps.services.party import party_service
from byceps.services.shop.shop import shop_service
from byceps.services.shop.storefront import storefront_service
from byceps.services.site import site_service
from byceps.util.forms import MultiCheckboxField
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )
    server_name = StringField(
        lazy_gettext('Server name'), validators=[InputRequired()]
    )
    party_id = SelectField(lazy_gettext('Party'), validators=[Optional()])
    enabled = BooleanField(lazy_gettext('enabled'))
    user_account_creation_enabled = BooleanField(
        lazy_gettext('User registration open')
    )
    login_enabled = BooleanField(lazy_gettext('User login open'))
    board_id = SelectField(lazy_gettext('Board ID'), validators=[Optional()])
    storefront_id = SelectField(
        lazy_gettext('Storefront ID'), validators=[Optional()]
    )
    is_intranet = BooleanField(lazy_gettext('Use as intranet'))
    check_in_on_login = BooleanField(
        lazy_gettext('Check in attendees on login to this site')
    )

    def set_party_choices(self, brand_id):
        parties = party_service.get_parties_for_brand(brand_id)
        parties.sort(key=lambda party: party.starts_at, reverse=True)

        choices = [(p.id, p.title) for p in parties]
        choices.insert(0, ('', '<' + pgettext('party', 'none') + '>'))
        self.party_id.choices = choices

    def set_board_choices(self, brand_id):
        boards = board_service.get_boards_for_brand(brand_id)
        boards.sort(key=lambda board: board.id)

        choices = [(b.id, b.id) for b in boards]
        choices.insert(0, ('', '<' + pgettext('board', 'none') + '>'))
        self.board_id.choices = choices

    def set_storefront_choices(self, brand_id):
        shop = shop_service.find_shop_for_brand(brand_id)
        if shop:
            storefronts = list(
                storefront_service.get_storefronts_for_shop(shop.id)
            )
            storefronts.sort(key=lambda storefront: storefront.id)

            choices = [(s.id, s.id) for s in storefronts]
        else:
            choices = []

        choices.insert(0, ('', '<' + pgettext('storefront', 'none') + '>'))
        self.storefront_id.choices = choices


class CreateForm(_BaseForm):
    id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )

    @staticmethod
    def validate_id(form, field):
        site_id = field.data.strip()

        if site_service.find_site(site_id):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if not site_service.is_title_available(title):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )

    @staticmethod
    def validate_server_name(form, field):
        server_name = field.data.strip()

        if not site_service.is_server_name_available(server_name):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )


class UpdateForm(_BaseForm):
    archived = BooleanField(lazy_gettext('archived'))

    def __init__(
        self, current_title: str, current_server_name: str, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._current_title = current_title
        self._current_server_name = current_server_name

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if title != form._current_title and not site_service.is_title_available(
            title
        ):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )

    @staticmethod
    def validate_server_name(form, field):
        server_name = field.data.strip()

        if (
            server_name != form._current_server_name
            and not site_service.is_server_name_available(server_name)
        ):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )


class AssignNewsChannelsForm(LocalizedForm):
    news_channel_ids = MultiCheckboxField(
        lazy_gettext('News channels'), validators=[Optional()]
    )

    def set_news_channel_id_choices(self, brand_id):
        news_channels = news_channel_service.get_channels_for_brand(brand_id)

        news_channel_ids = [c.id for c in news_channels]
        news_channel_ids.sort()

        choices = [(channel_id, channel_id) for channel_id in news_channel_ids]
        self.news_channel_ids.choices = choices
