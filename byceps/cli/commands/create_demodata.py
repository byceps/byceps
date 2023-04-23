"""Populate the database with data for demonstration purposes.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

import click
from flask.cli import with_appcontext
from moneyed import EUR, Money

from byceps.services.authorization import authz_service
from byceps.services.board import board_category_command_service, board_service
from byceps.services.board.models import Board, BoardID
from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand
from byceps.services.page import page_service
from byceps.services.party import party_service
from byceps.services.party.models import Party
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
from byceps.services.user import user_command_service, user_creation_service
from byceps.services.user.models.user import User
from byceps.typing import BrandID, PartyID, UserID


@click.command()
@with_appcontext
def create_demodata() -> None:
    """Generate data for demonstration purposes."""
    admin = _create_admin()
    brand = _create_brand()
    party = _create_party(brand.id)
    board = _create_board(brand.id)
    ticket_category = _create_ticket_category(party.id)
    shop = _create_shop(brand.id)
    _create_shop_articles(shop.id, ticket_category)
    storefront = _create_shop_storefront(shop.id)
    site = _create_site(brand.id, party.id, board.id, storefront.id)
    _create_pages(site.id, admin.id)


def _create_admin() -> User:
    user, _ = user_creation_service.create_user(
        'DemoAdmin', 'admin@demo.example', 'demodemo', locale='en'
    ).unwrap()
    user_command_service.initialize_account(user.id)

    for role_id in authz_service.get_all_role_ids():
        authz_service.assign_role_to_user(role_id, user.id)

    return user


def _create_brand() -> Brand:
    click.echo('Creating brand ... ', nl=False)
    brand = brand_service.create_brand(BrandID('cozylan'), 'CozyLAN')
    click.secho('done. ', fg='green')
    return brand


def _create_party(brand_id: BrandID) -> Party:
    click.echo('Creating party ... ', nl=False)
    party = party_service.create_party(
        PartyID('cozylan-2023'),
        brand_id,
        'CozyLAN 2023',
        datetime(2023, 6, 23, 16, 0),
        datetime(2023, 6, 25, 13, 0),
        max_ticket_quantity=120,
        ticket_management_enabled=True,
        seat_management_enabled=True,
    )
    click.secho('done. ', fg='green')
    return party


def _create_board(brand_id: BrandID) -> Board:
    click.echo('Creating board ... ', nl=False)
    board = board_service.create_board(brand_id, BoardID('cozylan'))
    click.secho('done. ', fg='green')

    click.echo('Creating board categories ... ', nl=False)
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
    click.secho('done. ', fg='green')

    return board


def _create_ticket_category(party_id: PartyID) -> TicketCategory:
    return ticket_category_service.create_category(party_id, 'Standard')


def _create_shop(brand_id: BrandID) -> Shop:
    click.echo('Creating shop ... ', nl=False)
    shop = shop_service.create_shop(
        ShopID('cozylan'), brand_id, 'CozyLAN Shop', EUR
    )
    click.secho('done. ', fg='green')
    return shop


def _create_shop_articles(
    shop_id: ShopID, ticket_category: TicketCategory
) -> None:
    click.echo('Creating shop articles ... ', nl=False)

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

    click.secho('done. ', fg='green')


def _create_shop_storefront(shop_id: ShopID) -> Storefront:
    click.echo('Creating shop storefront ... ', nl=False)
    order_number_sequence_id = (
        order_sequence_service.create_order_number_sequence(
            shop_id, 'O-CL2023-'
        )
        .unwrap()
        .id
    )
    storefront = storefront_service.create_storefront(
        StorefrontID('cozylan'), shop_id, order_number_sequence_id, closed=False
    )
    click.secho('done. ', fg='green')
    return storefront


def _create_site(
    brand_id: BrandID,
    party_id: PartyID,
    board_id: BoardID,
    storefront_id: StorefrontID,
) -> Site:
    click.echo('Creating site ... ', nl=False)
    site = site_service.create_site(
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
    click.secho('done. ', fg='green')
    return site


def _create_pages(site_id: SiteID, creator_id: UserID) -> None:
    page_service.create_page(
        site_id,
        'imprint',
        'en',
        '/imprint',
        creator_id,
        'Imprint',
        'Legal stuff goes here.',
    )

    page_service.create_page(
        site_id,
        'impressum',
        'de',
        '/impressum',
        creator_id,
        'Impressum',
        'Hier kommt das Impressum hin.',
    )

    nav_main_en = site_navigation_service.create_menu(site_id, 'main', 'en')
    nav_main_de = site_navigation_service.create_menu(site_id, 'main', 'de')

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
