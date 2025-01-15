"""
byceps.services.demo_data.demo_data_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Populate the database with data for demonstration purposes.

:Copyright: 2014-2025 Jochen Kupperschmidt
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
from byceps.services.shop.order import order_sequence_service
from byceps.services.shop.product import (
    product_sequence_service,
    product_service,
)
from byceps.services.shop.product.models import ProductType
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


BRAND_ID = BrandID('cozylan')
PARTY_ID = PartyID('cozylan-2023')
BOARD_ID = BoardID('cozylan')
SHOP_ID = ShopID('cozylan')
STOREFRONT_ID = StorefrontID('cozylan')


def create_demo_data(creator: User) -> None:
    """Generate data for demonstration purposes."""
    brand = _create_brand(creator)
    party = _create_party(brand.id)
    board = _create_board(brand)
    ticket_category = _create_ticket_category(party.id)
    shop = _create_shop(brand)
    _create_shop_products(shop.id, ticket_category)
    storefront = _create_shop_storefront(shop.id)
    site = _create_site(brand.id, party.id, board.id, storefront.id)
    _create_pages(site, creator)


def _create_brand(creator: User) -> Brand:
    log.info('Creating demo brand ...')
    brand = brand_service.create_brand(BRAND_ID, 'CozyLAN')

    log.info('Creating demo email configuration ...')
    email_config_service.create_config(brand.id, 'noreply@demo.example')

    log.info('Creating demo email footer snippets ...')
    email_footer_service.create_footers(brand, creator, 'info@demo.example')

    return brand


def _create_party(brand_id: BrandID) -> Party:
    log.info('Creating demo party ...')
    return party_service.create_party(
        PARTY_ID,
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
    board = board_service.create_board(brand, BOARD_ID)

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


def _create_shop(brand: Brand) -> Shop:
    log.info('Creating demo shop ...')
    return shop_service.create_shop(brand, EUR)


def _create_shop_products(
    shop_id: ShopID, ticket_category: TicketCategory
) -> None:
    log.info('Creating demo shop products ...')

    product_number_sequence = (
        product_sequence_service.create_product_number_sequence(
            shop_id, 'A-CL2023-'
        ).unwrap()
    )

    product_number_ticket = product_sequence_service.generate_product_number(
        product_number_sequence.id
    ).unwrap()
    product_service.create_ticket_product(
        shop_id,
        product_number_ticket,
        f'Ticket "{ticket_category.title}"',
        Money('35.00', EUR),
        Decimal('0.19'),
        120,
        5,
        ticket_category.id,
    )

    product_number_merch = product_sequence_service.generate_product_number(
        product_number_sequence.id
    ).unwrap()
    product_service.create_product(
        shop_id,
        product_number_merch,
        ProductType.physical,
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
        STOREFRONT_ID, shop_id, order_number_sequence_id, closed=False
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


def does_demo_data_exist() -> bool:
    """Try to figure out if demo data already exists.

    This check is likely incomplete, so do not rely on it too much.
    """
    brand_exists = brand_service.find_brand(BRAND_ID) is not None
    party_exists = party_service.find_party(PARTY_ID) is not None
    board_exists = board_service.find_board(BOARD_ID) is not None
    shop_exists = shop_service.find_shop(SHOP_ID) is not None
    storefront_exists = (
        storefront_service.find_storefront(STOREFRONT_ID) is not None
    )

    return (
        brand_exists
        or party_exists
        or board_exists
        or shop_exists
        or storefront_exists
    )
