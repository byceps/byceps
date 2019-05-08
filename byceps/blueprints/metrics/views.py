"""
byceps.blueprints.metrics
~~~~~~~~~~~~~~~~~~~~~~~~~

Metrics export for `Prometheus <https://prometheus.io/>`_

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Iterator, List

from flask import Response

from ...services.brand import service as brand_service
from ...services.board import board_service, \
    topic_query_service as board_topic_query_service, \
    posting_query_service as board_posting_query_service
from ...services.metrics.models import Label, Metric
from ...services.party import service as party_service
# Load order model so the ticket's foreign key can find the referenced table.
from ...services.shop.order.models import order
from ...services.shop.order import service as order_service
from ...services.shop.article import service as shop_article_service
from ...services.shop.shop import service as shop_service
from ...services.shop.shop.transfer.models import Shop
from ...services.ticketing import ticket_service
from ...services.user import stats_service as user_stats_service
from ...util.framework.blueprint import create_blueprint


blueprint = create_blueprint('metrics', __name__)


@blueprint.route('')
def metrics():
    """Return metrics."""
    data = list(_to_lines())

    return Response(data,
                    status=200,
                    mimetype='text/plain; version=0.0.4')


def _to_lines() -> Iterator[str]:
    for metric in _collect_metrics():
        yield metric.serialize() + '\n'


def _collect_metrics() -> Iterator[Metric]:
    brand_ids = [brand.id for brand in brand_service.get_brands()]
    active_shops = shop_service.get_active_shops()

    yield from _collect_board_metrics(brand_ids)
    yield from _collect_shop_article_metrics(active_shops)
    yield from _collect_shop_order_metrics(active_shops)
    yield from _collect_ticket_metrics()
    yield from _collect_user_metrics()


def _collect_board_metrics(brand_ids) -> Iterator[Metric]:
    for brand_id in brand_ids:
        boards = board_service.get_boards_for_brand(brand_id)
        board_ids = [board.id for board in boards]

        for board_id in board_ids:
            topic_count = board_topic_query_service \
                .count_topics_for_board(board_id)
            yield Metric('board_topic_count', topic_count,
                         labels=[Label('board', board_id)])

            posting_count = board_posting_query_service \
                .count_postings_for_board(board_id)
            yield Metric('board_posting_count', posting_count,
                         labels=[Label('board', board_id)])


def _collect_shop_article_metrics(shops: List[Shop]):
    """Provide article counts for shops."""
    for shop in shops:
        articles = shop_article_service.get_articles_for_shop(shop.id)
        for article in articles:
            yield Metric('shop_article_quantity', article.quantity,
                         labels=[
                             Label('shop', article.shop_id),
                             Label('item_number', article.item_number),
                         ])


def _collect_shop_order_metrics(shops: List[Shop]):
    """Provide order counts grouped by payment state for shops."""
    for shop in shops:
        order_counts_per_payment_state = order_service \
            .count_orders_per_payment_state(shop.id)

        for payment_state, quantity in order_counts_per_payment_state.items():
            yield Metric('shop_order_quantity', quantity,
                         labels=[
                             Label('shop', shop.id),
                             Label('payment_state', payment_state.name),
                         ])


def _collect_ticket_metrics() -> Iterator[Metric]:
    """Provide ticket counts for active parties."""
    active_parties = party_service.get_active_parties()
    active_party_ids = [p.id for p in active_parties]

    for party_id in active_party_ids:
        tickets_revoked_count = ticket_service \
            .count_revoked_tickets_for_party(party_id)
        yield Metric('tickets_revoked_count', tickets_revoked_count,
                     labels=[Label('party', party_id)])


        tickets_sold_count = ticket_service.count_tickets_for_party(party_id)
        yield Metric('tickets_sold_count', tickets_sold_count,
                     labels=[Label('party', party_id)])

        tickets_checked_in_count = ticket_service \
            .count_tickets_checked_in_for_party(party_id)
        yield Metric('tickets_checked_in_count', tickets_checked_in_count,
                     labels=[Label('party', party_id)])


def _collect_user_metrics() -> Iterator[Metric]:
    users_enabled = user_stats_service.count_enabled_users()
    users_disabled = user_stats_service.count_disabled_users()
    users_suspended = user_stats_service.count_suspended_users()
    users_deleted = user_stats_service.count_deleted_users()
    users_total = users_enabled + users_disabled

    yield Metric('users_enabled_count', users_enabled)
    yield Metric('users_disabled_count', users_disabled)
    yield Metric('users_suspended_count', users_suspended)
    yield Metric('users_deleted_count', users_deleted)
    yield Metric('users_total_count', users_total)
