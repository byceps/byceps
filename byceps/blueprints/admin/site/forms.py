"""
byceps.blueprints.admin.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext, pgettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from ....services.board import board_service
from ....services.brand import brand_service
from ....services.news import news_channel_service
from ....services.party import party_service
from ....services.shop.storefront import storefront_service
from ....util.l10n import LocalizedForm


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

    def set_storefront_choices(self):
        storefronts = storefront_service.get_all_storefronts()
        storefronts.sort(key=lambda storefront: storefront.id)

        choices = [(s.id, s.id) for s in storefronts]
        choices.insert(0, ('', '<' + pgettext('storefront', 'none') + '>'))
        self.storefront_id.choices = choices


class CreateForm(_BaseForm):
    id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )


class UpdateForm(_BaseForm):
    brand_id = SelectField(lazy_gettext('Brand'), validators=[InputRequired()])
    archived = BooleanField(lazy_gettext('archived'))

    def set_brand_choices(self):
        brands = brand_service.get_all_brands()
        brands.sort(key=lambda brand: brand.title)
        self.brand_id.choices = [(brand.id, brand.title) for brand in brands]


class AddNewsChannelForm(LocalizedForm):
    news_channel_id = SelectField(
        lazy_gettext('News channel ID'), validators=[InputRequired()]
    )

    def set_news_channel_choices(self, brand_id):
        news_channels = news_channel_service.get_channels_for_brand(brand_id)
        news_channels.sort(key=lambda channel: channel.id)

        choices = [(c.id, c.id) for c in news_channels]
        self.news_channel_id.choices = choices
