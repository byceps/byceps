"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.tourney.events import EventTourney, EventTourneyParticipant
from byceps.services.webhooks.models import (
    OutgoingWebhook,
    OutgoingWebhookFormat,
    WebhookID,
)

from tests.helpers import generate_token, generate_uuid


@pytest.fixture(scope='session')
def make_event_tourney():
    def _wrapper(
        *,
        id: str | None = None,
        title: str | None = None,
    ) -> EventTourney:
        if id is None:
            id = str(generate_uuid())

        if title is None:
            title = generate_token()

        return EventTourney(
            id=id,
            title=title,
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_event_tourney_participant():
    def _wrapper(
        *,
        id: str | None = None,
        name: str | None = None,
    ) -> EventTourneyParticipant:
        if id is None:
            id = str(generate_uuid())

        if name is None:
            name = generate_token()

        return EventTourneyParticipant(
            id=id,
            name=name,
        )

    return _wrapper


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
            'whereabouts-client-approved',
            'whereabouts-client-deleted',
            'whereabouts-client-registered',
            'whereabouts-client-signed-on',
            'whereabouts-client-signed-off',
            'whereabouts-status-updated',
        },
        event_filters={},
        format=OutgoingWebhookFormat.weitersager,
        text_prefix=None,
        extra_fields={'channel': '#eventlog'},
        url='http://127.0.0.1:12345/',
        description=None,
        enabled=True,
    )
