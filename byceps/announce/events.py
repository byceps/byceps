"""
byceps.announce.events
~~~~~~~~~~~~~~~~~~~~~~

Mapping between event types and names.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.events.auth import UserLoggedInEvent
from byceps.events.base import _BaseEvent
from byceps.events.board import (
    BoardPostingCreatedEvent,
    BoardPostingHiddenEvent,
    BoardPostingUnhiddenEvent,
    BoardTopicCreatedEvent,
    BoardTopicHiddenEvent,
    BoardTopicLockedEvent,
    BoardTopicMovedEvent,
    BoardTopicPinnedEvent,
    BoardTopicUnhiddenEvent,
    BoardTopicUnlockedEvent,
    BoardTopicUnpinnedEvent,
)
from byceps.events.guest_server import GuestServerRegisteredEvent
from byceps.events.news import NewsItemPublishedEvent
from byceps.events.page import (
    PageCreatedEvent,
    PageDeletedEvent,
    PageUpdatedEvent,
)
from byceps.events.shop import (
    ShopOrderCanceledEvent,
    ShopOrderPaidEvent,
    ShopOrderPlacedEvent,
)
from byceps.events.snippet import (
    SnippetCreatedEvent,
    SnippetDeletedEvent,
    SnippetUpdatedEvent,
)
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.events.tourney import (
    TourneyCanceledEvent,
    TourneyFinishedEvent,
    TourneyMatchReadyEvent,
    TourneyMatchResetEvent,
    TourneyMatchScoreConfirmedEvent,
    TourneyMatchScoreRandomizedEvent,
    TourneyMatchScoreSubmittedEvent,
    TourneyParticipantDisqualifiedEvent,
    TourneyParticipantEliminatedEvent,
    TourneyParticipantReadyEvent,
    TourneyParticipantWarnedEvent,
    TourneyPausedEvent,
    TourneyStartedEvent,
)
from byceps.events.user import (
    UserAccountCreatedEvent,
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserEmailAddressInvalidatedEvent,
    UserScreenNameChangedEvent,
)
from byceps.events.user_badge import UserBadgeAwarded


EVENT_TYPES_TO_NAMES = {
    UserLoggedInEvent: 'user-logged-in',
    BoardPostingCreatedEvent: 'board-posting-created',
    BoardPostingHiddenEvent: 'board-posting-hidden',
    BoardPostingUnhiddenEvent: 'board-posting-unhidden',
    BoardTopicCreatedEvent: 'board-topic-created',
    BoardTopicHiddenEvent: 'board-topic-hidden',
    BoardTopicLockedEvent: 'board-topic-locked',
    BoardTopicMovedEvent: 'board-topic-moved',
    BoardTopicPinnedEvent: 'board-topic-pinned',
    BoardTopicUnhiddenEvent: 'board-topic-unhidden',
    BoardTopicUnlockedEvent: 'board-topic-unlocked',
    BoardTopicUnpinnedEvent: 'board-topic-unpinned',
    GuestServerRegisteredEvent: 'guest-server-registered',
    NewsItemPublishedEvent: 'news-item-published',
    PageCreatedEvent: 'page-created',
    PageDeletedEvent: 'page-deleted',
    PageUpdatedEvent: 'page-updated',
    ShopOrderCanceledEvent: 'shop-order-canceled',
    ShopOrderPaidEvent: 'shop-order-paid',
    ShopOrderPlacedEvent: 'shop-order-placed',
    SnippetCreatedEvent: 'snippet-created',
    SnippetDeletedEvent: 'snippet-deleted',
    SnippetUpdatedEvent: 'snippet-updated',
    TicketCheckedInEvent: 'ticket-checked-in',
    TicketsSoldEvent: 'tickets-sold',
    TourneyCanceledEvent: 'tourney-canceled',
    TourneyFinishedEvent: 'tourney-finished',
    TourneyPausedEvent: 'tourney-paused',
    TourneyStartedEvent: 'tourney-started',
    TourneyMatchReadyEvent: 'tourney-match-ready',
    TourneyMatchResetEvent: 'tourney-match-reset',
    TourneyMatchScoreConfirmedEvent: 'tourney-match-score-confirmed',
    TourneyMatchScoreRandomizedEvent: 'tourney-match-score-randomized',
    TourneyMatchScoreSubmittedEvent: 'tourney-match-score-submitted',
    TourneyParticipantDisqualifiedEvent: 'tourney-participant-disqualified',
    TourneyParticipantEliminatedEvent: 'tourney-participant-eliminated',
    TourneyParticipantReadyEvent: 'tourney-participant-ready',
    TourneyParticipantWarnedEvent: 'tourney-participant-warned',
    UserAccountCreatedEvent: 'user-account-created',
    UserAccountDeletedEvent: 'user-account-deleted',
    UserAccountSuspendedEvent: 'user-account-suspended',
    UserAccountUnsuspendedEvent: 'user-account-unsuspended',
    UserBadgeAwarded: 'user-badge-awarded',
    UserDetailsUpdatedEvent: 'user-details-updated',
    UserEmailAddressChangedEvent: 'user-email-address-changed',
    UserEmailAddressInvalidatedEvent: 'user-email-address-invalidated',
    UserScreenNameChangedEvent: 'user-screen-name-changed',
}


def get_name_for_event(event: _BaseEvent) -> str:
    """Return the name for the event type.

    Raise exception if no name is defined for the event type.
    """
    event_type = type(event)
    return EVENT_TYPES_TO_NAMES[event_type]
