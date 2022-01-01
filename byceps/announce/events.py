"""
byceps.announce.events
~~~~~~~~~~~~~~~~~~~~~~

Mapping between event types and names.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..events.auth import UserLoggedIn
from ..events.base import _BaseEvent
from ..events.board import (
    BoardPostingCreated,
    BoardPostingHidden,
    BoardPostingUnhidden,
    BoardTopicCreated,
    BoardTopicHidden,
    BoardTopicLocked,
    BoardTopicMoved,
    BoardTopicPinned,
    BoardTopicUnhidden,
    BoardTopicUnlocked,
    BoardTopicUnpinned,
)
from ..events.guest_server import GuestServerRegistered
from ..events.news import NewsItemPublished
from ..events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ..events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ..events.ticketing import TicketCheckedIn, TicketsSold
from ..events.tourney import (
    TourneyStarted,
    TourneyPaused,
    TourneyCanceled,
    TourneyFinished,
    TourneyMatchReady,
    TourneyMatchReset,
    TourneyMatchScoreSubmitted,
    TourneyMatchScoreConfirmed,
    TourneyMatchScoreRandomized,
    TourneyParticipantReady,
    TourneyParticipantEliminated,
    TourneyParticipantWarned,
    TourneyParticipantDisqualified,
)
from ..events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressChanged,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from ..events.user_badge import UserBadgeAwarded


EVENT_TYPES_TO_NAMES = {
    UserLoggedIn:                   'user-logged-in',
    BoardTopicCreated:              'board-topic-created',
    BoardTopicHidden:               'board-topic-hidden',
    BoardTopicLocked:               'board-topic-locked',
    BoardTopicMoved:                'board-topic-moved',
    BoardTopicPinned:               'board-topic-pinned',
    BoardTopicUnhidden:             'board-topic-unhidden',
    BoardTopicUnlocked:             'board-topic-unlocked',
    BoardTopicUnpinned:             'board-topic-unpinned',
    BoardPostingCreated:            'board-posting-created',
    BoardPostingHidden:             'board-posting-hidden',
    BoardPostingUnhidden:           'board-posting-unhidden',
    GuestServerRegistered:          'guest-server-registered',
    NewsItemPublished:              'news-item-published',
    ShopOrderCanceled:              'shop-order-canceled',
    ShopOrderPaid:                  'shop-order-paid',
    ShopOrderPlaced:                'shop-order-placed',
    SnippetCreated:                 'snippet-created',
    SnippetDeleted:                 'snippet-deleted',
    SnippetUpdated:                 'snippet-updated',
    TicketCheckedIn:                'ticket-checked-in',
    TicketsSold:                    'tickets-sold',
    TourneyStarted:                 'tourney-started',
    TourneyPaused:                  'tourney-paused',
    TourneyCanceled:                'tourney-canceled',
    TourneyFinished:                'tourney-finished',
    TourneyMatchReady:              'tourney-match-ready',
    TourneyMatchReset:              'tourney-match-reset',
    TourneyMatchScoreSubmitted:     'tourney-match-score-submitted',
    TourneyMatchScoreConfirmed:     'tourney-match-score-confirmed',
    TourneyMatchScoreRandomized:    'tourney-match-score-randomized',
    TourneyParticipantReady:        'tourney-participant-ready',
    TourneyParticipantEliminated:   'tourney-participant-eliminated',
    TourneyParticipantWarned:       'tourney-participant-warned',
    TourneyParticipantDisqualified: 'tourney-participant-disqualified',
    UserAccountCreated:             'user-account-created',
    UserAccountDeleted:             'user-account-deleted',
    UserAccountSuspended:           'user-account-suspended',
    UserAccountUnsuspended:         'user-account-unsuspended',
    UserDetailsUpdated:             'user-details-updated',
    UserEmailAddressChanged:        'user-email-address-changed',
    UserEmailAddressInvalidated:    'user-email-address-invalidated',
    UserScreenNameChanged:          'user-screen-name-changed',
    UserBadgeAwarded:               'user-badge-awarded',
}


def get_name_for_event(event: _BaseEvent) -> str:
    """Return the name for the event type.

    Raise exception if no name is defined for the event type.
    """
    event_type = type(event)
    return EVENT_TYPES_TO_NAMES[event_type]
