"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.webhooks.models import OutgoingWebhook, WebhookID

from tests.helpers import generate_uuid


@pytest.fixture(scope='package')
def webhook_for_irc() -> OutgoingWebhook:
    return OutgoingWebhook(
        id=WebhookID(generate_uuid()),
        event_types={
            'board-topic-created',
            'board-topic-hidden',
            'board-topic-locked',
            'board-topic-moved',
            'board-topic-pinned',
            'board-topic-unhidden',
            'board-topic-unlocked',
            'board-topic-unpinned',
            'board-posting-created',
            'board-posting-hidden',
            'board-posting-unhidden',
            'guest-server-registered',
            'news-item-published',
            'page-created',
            'page-deleted',
            'page-updated',
            'shop-order-canceled',
            'shop-order-paid',
            'shop-order-placed',
            'snippet-created',
            'snippet-deleted',
            'snippet-updated',
            'ticket-checked-in',
            'tickets-sold',
            'tourney-started',
            'tourney-paused',
            'tourney-canceled',
            'tourney-finished',
            'tourney-match-ready',
            'tourney-match-reset',
            'tourney-match-score-submitted',
            'tourney-match-score-confirmed',
            'tourney-match-score-randomized',
            'tourney-participant-ready',
            'tourney-participant-eliminated',
            'tourney-participant-warned',
            'tourney-participant-disqualified',
            'user-account-created',
            'user-account-deleted',
            'user-account-suspended',
            'user-account-unsuspended',
            'user-badge-awarded',
            'user-details-updated',
            'user-email-address-changed',
            'user-email-address-invalidated',
            'user-screen-name-changed',
            'user-logged-in',
        },
        event_filters={},
        format='weitersager',
        text_prefix=None,
        extra_fields={'channel': '#eventlog'},
        url='http://127.0.0.1:12345/',
        description='',
        enabled=True,
    )
