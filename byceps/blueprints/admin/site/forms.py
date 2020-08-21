"""
byceps.blueprints.admin.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from ....util.l10n import LocalizedForm

from ....services.board import board_service
from ....services.brand import service as brand_service
from ....services.email import service as email_service
from ....services.news import channel_service as news_channel_service
from ....services.party import service as party_service
from ....services.shop.storefront import service as storefront_service


class _BaseForm(LocalizedForm):
    title = StringField('Titel', validators=[Length(min=1, max=40)])
    server_name = StringField('Servername', validators=[InputRequired()])
    email_config_id = SelectField('E-Mail-Konfiguration', validators=[InputRequired()])
    party_id = SelectField('Party', validators=[Optional()])
    enabled = BooleanField('aktiv')
    user_account_creation_enabled  = BooleanField('Benutzerregistrierung geöffnet')
    login_enabled = BooleanField('Benutzeranmeldung geöffnet')
    news_channel_id = SelectField('Newskanal-ID', validators=[Optional()])
    board_id = SelectField('Forums-ID', validators=[Optional()])
    storefront_id = SelectField('Storefront-ID', validators=[Optional()])

    def set_brand_choices(self):
        brands = brand_service.get_brands()
        brands.sort(key=lambda brand: brand.title)
        self.brand_id.choices = [(brand.id, brand.title) for brand in brands]

    def set_email_config_choices(self):
        configs = email_service.get_all_configs()
        configs.sort(key=lambda config: config.id)
        self.email_config_id.choices = [(c.id, c.id) for c in configs]

    def set_party_choices(self, brand_id):
        parties = party_service.get_parties_for_brand(brand_id)
        parties.sort(key=lambda party: party.starts_at, reverse=True)

        choices = [(p.id, p.title) for p in parties]
        choices.insert(0, ('', '<keine>'))
        self.party_id.choices = choices

    def set_news_channel_choices(self, brand_id):
        news_channels = news_channel_service.get_channels_for_brand(brand_id)
        news_channels.sort(key=lambda channel: channel.id)

        choices = [(c.id, c.id) for c in news_channels]
        choices.insert(0, ('', '<keiner>'))
        self.news_channel_id.choices = choices

    def set_board_choices(self, brand_id):
        boards = board_service.get_boards_for_brand(brand_id)
        boards.sort(key=lambda board: board.id)

        choices = [(b.id, b.id) for b in boards]
        choices.insert(0, ('', '<keins>'))
        self.board_id.choices = choices

    def set_storefront_choices(self):
        storefronts = storefront_service.get_all_storefronts()
        storefronts.sort(key=lambda storefront: storefront.id)

        choices = [(s.id, s.id) for s in storefronts]
        choices.insert(0, ('', '<keiner>'))
        self.storefront_id.choices = choices


class CreateForm(_BaseForm):
    id = StringField('ID', validators=[Length(min=1, max=40)])


class UpdateForm(_BaseForm):
    brand_id = SelectField('Marke', validators=[InputRequired()])
    archived = BooleanField('archiviert')
