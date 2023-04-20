"""
byceps.metrics.metrics_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator

from byceps.services.board import (
    board_posting_query_service,
    board_service,
    board_topic_query_service,
)
from byceps.services.brand import brand_service
from byceps.services.consent import consent_service
from byceps.services.metrics.models import Label, Metric
from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.seating import seat_service
from byceps.services.shop.article import article_service as shop_article_service
from byceps.services.shop.order import order_service
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.services.ticketing import ticket_service
from byceps.services.user import user_stats_service
from byceps.typing import BrandID, PartyID


def serialize(metrics: Iterator[Metric]) -> Iterator[str]:
    """Serialize metric objects to text lines."""
    for metric in metrics:
        yield metric.serialize() + '\n'


def collect_metrics() -> Iterator[Metric]:
    brand_ids = [brand.id for brand in brand_service.get_all_brands()]

    active_parties = party_service.get_active_parties()
    active_party_ids = [p.id for p in active_parties]

    active_shops = shop_service.get_active_shops()
    active_shop_ids = {shop.id for shop in active_shops}

    yield from _collect_board_metrics(brand_ids)
    yield from _collect_consent_metrics()
    yield from _collect_shop_ordered_article_metrics(active_shop_ids)
    yield from _collect_shop_order_metrics(active_shops)
    yield from _collect_seating_metrics(active_party_ids)
    yield from _collect_ticket_metrics(active_parties)
    yield from _collect_user_metrics()


def _collect_board_metrics(brand_ids: list[BrandID]) -> Iterator[Metric]:
    for brand_id in brand_ids:
        boards = board_service.get_boards_for_brand(brand_id)
        board_ids = [board.id for board in boards]

        for board_id in board_ids:
            labels = [Label('board', board_id)]

            topic_count = board_topic_query_service.count_topics_for_board(
                board_id
            )
            yield Metric('board_topic_count', topic_count, labels=labels)

            posting_count = (
                board_posting_query_service.count_postings_for_board(board_id)
            )
            yield Metric('board_posting_count', posting_count, labels=labels)


def _collect_consent_metrics() -> Iterator[Metric]:
    consents_per_subject = consent_service.count_consents_by_subject()
    for subject_name, consent_count in consents_per_subject.items():
        yield Metric(
            'consent_count',
            consent_count,
            labels=[Label('subject_name', subject_name)],
        )


def _collect_shop_ordered_article_metrics(
    shop_ids: set[ShopID],
) -> Iterator[Metric]:
    """Provide ordered article quantities for shops."""
    stats = shop_article_service.sum_ordered_articles_by_payment_state(shop_ids)

    for shop_id, article_number, description, payment_state, quantity in stats:
        yield Metric(
            'shop_ordered_article_quantity',
            quantity,
            labels=[
                Label('shop', shop_id),
                Label('article_number', article_number),
                Label('description', description),
                Label('payment_state', payment_state.name),
            ],
        )


def _collect_shop_order_metrics(shops: list[Shop]) -> Iterator[Metric]:
    """Provide order counts grouped by payment state for shops."""
    for shop in shops:
        order_counts_per_payment_state = (
            order_service.count_orders_per_payment_state(shop.id)
        )

        for payment_state, quantity in order_counts_per_payment_state.items():
            yield Metric(
                'shop_order_quantity',
                quantity,
                labels=[
                    Label('shop', shop.id),
                    Label('payment_state', payment_state.name),
                ],
            )


def _collect_seating_metrics(
    active_party_ids: list[PartyID],
) -> Iterator[Metric]:
    """Provide seat occupation counts per party and category."""
    for party_id in active_party_ids:
        occupied_seat_counts_by_category = (
            seat_service.count_occupied_seats_by_category(party_id)
        )

        for category, count in occupied_seat_counts_by_category:
            yield Metric(
                'occupied_seat_count',
                count,
                labels=[
                    Label('party', party_id),
                    Label('category_title', category.title),
                ],
            )


def _collect_ticket_metrics(active_parties: list[Party]) -> Iterator[Metric]:
    """Provide ticket counts for active parties."""
    for party in active_parties:
        party_id = party.id
        labels = [Label('party', party_id)]

        max_ticket_quantity = party.max_ticket_quantity
        if max_ticket_quantity is not None:
            yield Metric('tickets_max', max_ticket_quantity, labels=labels)

        tickets_revoked_count = ticket_service.count_revoked_tickets_for_party(
            party_id
        )
        yield Metric(
            'tickets_revoked_count', tickets_revoked_count, labels=labels
        )

        tickets_sold_count = ticket_service.count_sold_tickets_for_party(
            party_id
        )
        yield Metric('tickets_sold_count', tickets_sold_count, labels=labels)

        tickets_checked_in_count = (
            ticket_service.count_tickets_checked_in_for_party(party_id)
        )
        yield Metric(
            'tickets_checked_in_count', tickets_checked_in_count, labels=labels
        )


def _collect_user_metrics() -> Iterator[Metric]:
    users_active = user_stats_service.count_active_users()
    users_uninitialized = user_stats_service.count_uninitialized_users()
    users_suspended = user_stats_service.count_suspended_users()
    users_deleted = user_stats_service.count_deleted_users()
    users_total = user_stats_service.count_users()

    yield Metric('users_active_count', users_active)
    yield Metric('users_uninitialized_count', users_uninitialized)
    yield Metric('users_suspended_count', users_suspended)
    yield Metric('users_deleted_count', users_deleted)
    yield Metric('users_total_count', users_total)
