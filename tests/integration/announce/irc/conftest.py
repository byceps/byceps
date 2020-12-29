"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.webhooks import service as webhook_service

from .helpers import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@pytest.fixture(scope='module')
def webhook_settings():
    event_selectors = set(
        [
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
            'news-item-published',
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
            'user-details-updated',
            'user-email-address-invalidated',
            'user-screen-name-changed',
            'user-badge-awarded',
        ]
    )
    scopes_and_channels = [
        ('internal', CHANNEL_ORGA_LOG),
        ('public', CHANNEL_PUBLIC),
    ]
    scope_id = None
    format = 'weitersager'
    url = 'http://127.0.0.1:12345/'
    enabled = True

    webhooks = [
        webhook_service.create_outgoing_webhook(
            event_selectors,
            scope,
            scope_id,
            format,
            url,
            enabled,
            extra_fields={'channel': channel},
        )
        for scope, channel in scopes_and_channels
    ]

    yield

    for webhook in webhooks:
        webhook_service.delete_outgoing_webhook(webhook.id)


@pytest.fixture(scope='module')
def app(admin_app, webhook_settings):
    return admin_app
