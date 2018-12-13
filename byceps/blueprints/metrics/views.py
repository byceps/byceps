"""
byceps.blueprints.metrics
~~~~~~~~~~~~~~~~~~~~~~~~~

Metrics export for `Prometheus <https://prometheus.io/>`_

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import Response

from ...services.brand import service as brand_service
from ...services.board import board_service, \
    topic_service as board_topic_service, \
    posting_service as board_posting_service
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


def _to_lines():
    for metric_name, value in _collect_metrics():
        yield metric_name + ' ' + str(value) + '\n'


def _collect_metrics():
    brand_ids = [brand.id for brand in brand_service.get_brands()]

    yield from _collect_board_metrics(brand_ids)
    yield from _collect_ticket_metrics()
    yield from _collect_user_metrics()


def _collect_board_metrics(brand_ids):
    for brand_id in brand_ids:
        boards = board_service.get_boards_for_brand(brand_id)
        board_ids = [board.id for board in boards]

        for board_id in board_ids:
            topic_count = board_topic_service.count_topics_for_board(board_id)
            yield 'board_topic_count{{board="{}"}}'.format(board_id), \
                topic_count

            posting_count = board_posting_service \
                .count_postings_for_board(board_id)
            yield 'board_posting_count{{board="{}"}}'.format(board_id), \
                posting_count


def _collect_ticket_metrics():
    ticket_counts_by_party_id = ticket_service.get_ticket_count_by_party_id()
    for party_id, count in ticket_counts_by_party_id.items():
        yield 'ticket_count{{party="{}"}}'.format(party_id), count


def _collect_user_metrics():
    users_enabled = user_stats_service.count_enabled_users()
    users_disabled = user_stats_service.count_disabled_users()
    users_suspended = user_stats_service.count_suspended_users()
    users_deleted = user_stats_service.count_deleted_users()
    users_total = users_enabled + users_disabled

    yield 'users_enabled_count', users_enabled
    yield 'users_disabled_count', users_disabled
    yield 'users_suspended_count', users_suspended
    yield 'users_deleted_count', users_deleted
    yield 'users_total_count', users_total
