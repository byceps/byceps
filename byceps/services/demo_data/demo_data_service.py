"""
byceps.services.demo_data.demo_data_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Populate the database with data for demonstration purposes.

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from moneyed import EUR, Money
import structlog

from byceps.services.board import board_category_command_service, board_service
from byceps.services.board.models import Board, BoardID
from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand, BrandID
from byceps.services.email import email_config_service, email_footer_service
from byceps.services.page import page_service
from byceps.services.party import party_service
from byceps.services.party.models import Party, PartyID
from byceps.services.shop.article import (
    article_sequence_service,
    article_service,
)
from byceps.services.shop.article.models import ArticleType
from byceps.services.shop.order import order_sequence_service
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.services.shop.storefront import storefront_service
from byceps.services.shop.storefront.models import Storefront, StorefrontID
from byceps.services.site import site_service
from byceps.services.site.models import Site, SiteID
from byceps.services.site_navigation import site_navigation_service
from byceps.services.site_navigation.models import NavItemTargetType
from byceps.services.ticketing import ticket_category_service
from byceps.services.ticketing.models.ticket import TicketCategory
from byceps.services.user.models.user import User


log = structlog.get_logger()


def create_demo_data(creator: User) -> None:
    """Generate data for demonstration purposes."""
    brand = _create_brand(creator)
    party = _create_party(brand.id)
    board = _create_board(brand)
    ticket_category = _create_ticket_category(party.id)
    shop = _create_shop(brand.id)
    _create_shop_articles(shop.id, ticket_category)
    storefront = _create_shop_storefront(shop.id)
    site = _create_site(brand.id, party.id, board.id, storefront.id)
    _create_pages(site, creator)


def _create_brand(creator: User) -> Brand:
    log.info('Creating demo brand ...')
    brand = brand_service.create_brand(BrandID('cozylan'), 'CozyLAN')

    log.info('Creating demo email configuration ...')
    email_config_service.create_config(brand.id, 'noreply@demo.example')

    log.info('Creating demo email footer snippets ...')
    email_footer_service.create_footers(brand, creator, 'info@demo.example')

    return brand


def _create_party(brand_id: BrandID) -> Party:
    log.info('Creating demo party ...')
    return party_service.create_party(
        PartyID('cozylan-2023'),
        brand_id,
        'CozyLAN 2023',
        datetime(2023, 6, 23, 16, 0),
        datetime(2023, 6, 25, 13, 0),
        max_ticket_quantity=120,
        ticket_management_enabled=True,
        seat_management_enabled=True,
    )


def _create_board(brand: Brand) -> Board:
    log.info('Creating demo board ...')
    board = board_service.create_board(brand, BoardID('cozylan'))

    log.info('Creating demo board categories ...')
    for slug, title, description in [
        (
            'general',
            'General',
            'General party-related questions and discussions',
        ),
        ('car-sharing', 'Car Sharing', 'Need a ride or have free seats?'),
        ('off-topic', 'Off-Topic', 'Everything else'),
    ]:
        board_category_command_service.create_category(
            board.id, slug, title, description
        )

    return board


def _create_ticket_category(party_id: PartyID) -> TicketCategory:
    return ticket_category_service.create_category(party_id, 'Standard')


def _create_shop(brand_id: BrandID) -> Shop:
    log.info('Creating demo shop ...')
    return shop_service.create_shop(
        ShopID('cozylan'), brand_id, 'CozyLAN Shop', EUR
    )


def _create_shop_articles(
    shop_id: ShopID, ticket_category: TicketCategory
) -> None:
    log.info('Creating demo shop articles ...')

    article_number_sequence = (
        article_sequence_service.create_article_number_sequence(
            shop_id, 'A-CL2023-'
        ).unwrap()
    )

    article_number_ticket = article_sequence_service.generate_article_number(
        article_number_sequence.id
    ).unwrap()
    article_service.create_ticket_article(
        shop_id,
        article_number_ticket,
        f'Ticket "{ticket_category.title}"',
        Money('35.00', EUR),
        Decimal('0.19'),
        120,
        5,
        ticket_category.id,
    )

    article_number_merch = article_sequence_service.generate_article_number(
        article_number_sequence.id
    ).unwrap()
    article_service.create_article(
        shop_id,
        article_number_merch,
        ArticleType.physical,
        'Sticker Pack',
        Money('5.00', EUR),
        Decimal('0.19'),
        300,
        10,
        True,
    )


def _create_shop_storefront(shop_id: ShopID) -> Storefront:
    log.info('Creating demo shop storefront ...')

    order_number_sequence_id = (
        order_sequence_service.create_order_number_sequence(
            shop_id, 'O-CL2023-'
        )
        .unwrap()
        .id
    )

    return storefront_service.create_storefront(
        StorefrontID('cozylan'), shop_id, order_number_sequence_id, closed=False
    )


def _create_site(
    brand_id: BrandID,
    party_id: PartyID,
    board_id: BoardID,
    storefront_id: StorefrontID,
) -> Site:
    log.info('Creating demo site ...')
    return site_service.create_site(
        SiteID('cozylan'),
        'CozyLAN Website',
        'cozylan.example',
        brand_id,
        enabled=True,
        user_account_creation_enabled=True,
        login_enabled=True,
        party_id=party_id,
        board_id=board_id,
        storefront_id=storefront_id,
    )


def _create_pages(site: Site, creator: User) -> None:
    page_service.create_page(
        site,
        'imprint',
        'en',
        '/imprint',
        creator,
        'Imprint',
        'Legal stuff goes here.',
    )

    page_service.create_page(
        site,
        'impressum',
        'de',
        '/impressum',
        creator,
        'Impressum',
        'Hier kommt das Impressum hin.',
    )

    nav_main_en = site_navigation_service.create_menu(site.id, 'main', 'en')
    nav_main_de = site_navigation_service.create_menu(site.id, 'main', 'de')

    site_navigation_service.create_item(
        nav_main_en.id, NavItemTargetType.page, 'imprint', 'Imprint', 'imprint'
    ).unwrap()
    site_navigation_service.create_item(
        nav_main_de.id,
        NavItemTargetType.page,
        'imprint',
        'Impressum',
        'imprint',
    ).unwrap()
