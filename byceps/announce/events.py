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
from byceps.events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from byceps.events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from byceps.events.ticketing import TicketCheckedIn, TicketsSold
from byceps.events.tourney import (
    TourneyCanceled,
    TourneyFinished,
    TourneyMatchReady,
    TourneyMatchReset,
    TourneyMatchScoreConfirmed,
    TourneyMatchScoreRandomized,
    TourneyMatchScoreSubmitted,
    TourneyParticipantDisqualified,
    TourneyParticipantEliminated,
    TourneyParticipantReady,
    TourneyParticipantWarned,
    TourneyPaused,
    TourneyStarted,
)
from byceps.events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressChanged,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
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
    ShopOrderCanceled: 'shop-order-canceled',
    ShopOrderPaid: 'shop-order-paid',
    ShopOrderPlaced: 'shop-order-placed',
    SnippetCreated: 'snippet-created',
    SnippetDeleted: 'snippet-deleted',
    SnippetUpdated: 'snippet-updated',
    TicketCheckedIn: 'ticket-checked-in',
    TicketsSold: 'tickets-sold',
    TourneyCanceled: 'tourney-canceled',
    TourneyFinished: 'tourney-finished',
    TourneyPaused: 'tourney-paused',
    TourneyStarted: 'tourney-started',
    TourneyMatchReady: 'tourney-match-ready',
    TourneyMatchReset: 'tourney-match-reset',
    TourneyMatchScoreConfirmed: 'tourney-match-score-confirmed',
    TourneyMatchScoreRandomized: 'tourney-match-score-randomized',
    TourneyMatchScoreSubmitted: 'tourney-match-score-submitted',
    TourneyParticipantDisqualified: 'tourney-participant-disqualified',
    TourneyParticipantEliminated: 'tourney-participant-eliminated',
    TourneyParticipantReady: 'tourney-participant-ready',
    TourneyParticipantWarned: 'tourney-participant-warned',
    UserAccountCreated: 'user-account-created',
    UserAccountDeleted: 'user-account-deleted',
    UserAccountSuspended: 'user-account-suspended',
    UserAccountUnsuspended: 'user-account-unsuspended',
    UserBadgeAwarded: 'user-badge-awarded',
    UserDetailsUpdated: 'user-details-updated',
    UserEmailAddressChanged: 'user-email-address-changed',
    UserEmailAddressInvalidated: 'user-email-address-invalidated',
    UserScreenNameChanged: 'user-screen-name-changed',
}


def get_name_for_event(event: _BaseEvent) -> str:
    """Return the name for the event type.

    Raise exception if no name is defined for the event type.
    """
    event_type = type(event)
    return EVENT_TYPES_TO_NAMES[event_type]
