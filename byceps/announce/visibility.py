"""
byceps.announce.visibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

Visibility definitions of events

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum
from typing import Set

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
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from ..events.user_badge import UserBadgeAwarded


Visibility = Enum('Visibility', ['internal', 'public'])

INTERNAL = Visibility.internal
PUBLIC = Visibility.public


EVENT_VISIBILITIES = {
    BoardTopicCreated:              {INTERNAL, PUBLIC},
    BoardTopicHidden:               {INTERNAL},
    BoardTopicLocked:               {INTERNAL},
    BoardTopicMoved:                {INTERNAL},
    BoardTopicPinned:               {INTERNAL},
    BoardTopicUnhidden:             {INTERNAL},
    BoardTopicUnlocked:             {INTERNAL},
    BoardTopicUnpinned:             {INTERNAL},
    BoardPostingCreated:            {INTERNAL, PUBLIC},
    BoardPostingHidden:             {INTERNAL},
    BoardPostingUnhidden:           {INTERNAL},
    NewsItemPublished:              {INTERNAL, PUBLIC},
    ShopOrderCanceled:              {INTERNAL},
    ShopOrderPaid:                  {INTERNAL},
    ShopOrderPlaced:                {INTERNAL},
    SnippetCreated:                 {INTERNAL},
    SnippetDeleted:                 {INTERNAL},
    SnippetUpdated:                 {INTERNAL},
    TicketCheckedIn:                {INTERNAL},
    TicketsSold:                    {INTERNAL},
    TourneyStarted:                 {PUBLIC},
    TourneyPaused:                  {PUBLIC},
    TourneyCanceled:                {PUBLIC},
    TourneyFinished:                {PUBLIC},
    TourneyMatchReady:              {PUBLIC},
    TourneyMatchReset:              {PUBLIC},
    TourneyMatchScoreSubmitted:     {PUBLIC},
    TourneyMatchScoreConfirmed:     {PUBLIC},
    TourneyMatchScoreRandomized:    {PUBLIC},
    TourneyParticipantReady:        {PUBLIC},
    TourneyParticipantEliminated:   {PUBLIC},
    TourneyParticipantWarned:       {PUBLIC},
    TourneyParticipantDisqualified: {PUBLIC},
    UserAccountCreated:             {INTERNAL},
    UserAccountDeleted:             {INTERNAL},
    UserAccountSuspended:           {INTERNAL},
    UserAccountUnsuspended:         {INTERNAL},
    UserDetailsUpdated:             {INTERNAL},
    UserEmailAddressInvalidated:    {INTERNAL},
    UserScreenNameChanged:          {INTERNAL},
    UserBadgeAwarded:               {INTERNAL},
}


def get_visibilities(event: _BaseEvent) -> Set[Visibility]:
    """Return the visibility of events of this type."""
    event_type = type(event)
    return EVENT_VISIBILITIES.get(event_type, set())
