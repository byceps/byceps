"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.webhooks import service as webhook_service

from .helpers import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@pytest.fixture(scope='module')
def webhook_settings():
    event_selector_sets = [
        # internal
        dict.fromkeys(
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
                'guest-server-registered',
                'news-item-published',
                'shop-order-canceled',
                'shop-order-paid',
                'shop-order-placed',
                'snippet-created',
                'snippet-deleted',
                'snippet-updated',
                'ticket-checked-in',
                'tickets-sold',
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
            ]
        ),
        # public
        dict.fromkeys(
            [
                'board-topic-created',
                'board-posting-created',
                'news-item-published',
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
            ]
        ),
    ]
    channels = [CHANNEL_ORGA_LOG, CHANNEL_PUBLIC]
    format = 'weitersager'
    url = 'http://127.0.0.1:12345/'
    enabled = True

    webhooks = [
        webhook_service.create_outgoing_webhook(
            event_selectors,
            {},  # event_filters
            format,
            url,
            enabled,
            extra_fields={'channel': channel},
        )
        for event_selectors, channel in zip(event_selector_sets, channels)
    ]

    yield

    for webhook in webhooks:
        webhook_service.delete_outgoing_webhook(webhook.id)


@pytest.fixture(scope='module')
def app(admin_app, webhook_settings):
    return admin_app
