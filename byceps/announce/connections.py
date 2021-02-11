"""
byceps.announce.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect event signals to announcement handlers.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

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
from ..signals import auth as auth_signals
from ..signals import board as board_signals
from ..signals import news as news_signals
from ..signals import shop as shop_signals
from ..signals import snippet as snippet_signals
from ..signals import ticketing as ticketing_signals
from ..signals import tourney as tourney_signals
from ..signals import user as user_signals
from ..signals import user_badge as user_badge_signals
from ..util.jobqueue import enqueue

from .handlers import (
    auth,
    board,
    news,
    shop_order,
    snippet,
    ticketing,
    tourney,
    user,
    user_badge,
)
from .helpers import get_webhooks


EVENT_TYPES_TO_HANDLERS = {
    UserLoggedIn: auth.announce_user_logged_in,
    BoardTopicCreated: board.announce_board_topic_created,
    BoardTopicHidden: board.announce_board_topic_hidden,
    BoardTopicUnhidden: board.announce_board_topic_unhidden,
    BoardTopicLocked: board.announce_board_topic_locked,
    BoardTopicUnlocked: board.announce_board_topic_unlocked,
    BoardTopicPinned: board.announce_board_topic_pinned,
    BoardTopicUnpinned: board.announce_board_topic_unpinned,
    BoardTopicMoved: board.announce_board_topic_moved,
    BoardPostingCreated: board.announce_board_posting_created,
    BoardPostingHidden: board.announce_board_posting_hidden,
    BoardPostingUnhidden: board.announce_board_posting_unhidden,
    NewsItemPublished: news.announce_news_item_published,
    ShopOrderPlaced: shop_order.announce_order_placed,
    ShopOrderPaid: shop_order.announce_order_paid,
    ShopOrderCanceled: shop_order.announce_order_canceled,
    SnippetCreated: snippet.announce_snippet_created,
    SnippetUpdated: snippet.announce_snippet_updated,
    SnippetDeleted: snippet.announce_snippet_deleted,
    TicketCheckedIn: ticketing.announce_ticket_checked_in,
    TicketsSold: ticketing.announce_tickets_sold,
    TourneyStarted: tourney.announce_tourney_started,
    TourneyPaused: tourney.announce_tourney_paused,
    TourneyCanceled: tourney.announce_tourney_canceled,
    TourneyFinished: tourney.announce_tourney_finished,
    TourneyMatchReady: tourney.announce_match_ready,
    TourneyMatchReset: tourney.announce_match_reset,
    TourneyMatchScoreSubmitted: tourney.announce_match_score_submitted,
    TourneyMatchScoreConfirmed: tourney.announce_match_score_confirmed,
    TourneyMatchScoreRandomized: tourney.announce_match_score_randomized,
    TourneyParticipantReady: tourney.announce_participant_ready,
    TourneyParticipantEliminated: tourney.announce_participant_eliminated,
    TourneyParticipantWarned: tourney.announce_participant_warned,
    TourneyParticipantDisqualified: tourney.announce_participant_disqualified,
    UserAccountCreated: user.announce_user_account_created,
    UserScreenNameChanged: user.announce_user_screen_name_changed,
    UserEmailAddressInvalidated: user.announce_user_email_address_invalidated,
    UserDetailsUpdated: user.announce_user_details_updated_changed,
    UserAccountSuspended: user.announce_user_account_suspended,
    UserAccountUnsuspended: user.announce_user_account_unsuspended,
    UserAccountDeleted: user.announce_user_account_deleted,
    UserBadgeAwarded: user_badge.announce_user_badge_awarded,
}


def receive_signal(sender, *, event: Optional[_BaseEvent] = None) -> None:
    event_type = type(event)

    handler = EVENT_TYPES_TO_HANDLERS.get(event_type)
    if handler is None:
        return None

    webhooks = get_webhooks(event)
    for webhook in webhooks:
        enqueue(handler, event, webhook)


SIGNALS = [
    auth_signals.user_logged_in,
    board_signals.topic_created,
    board_signals.topic_hidden,
    board_signals.topic_unhidden,
    board_signals.topic_locked,
    board_signals.topic_unlocked,
    board_signals.topic_pinned,
    board_signals.topic_unpinned,
    board_signals.topic_moved,
    board_signals.posting_created,
    board_signals.posting_hidden,
    board_signals.posting_unhidden,
    news_signals.item_published,
    shop_signals.order_placed,
    shop_signals.order_paid,
    shop_signals.order_canceled,
    snippet_signals.snippet_created,
    snippet_signals.snippet_updated,
    snippet_signals.snippet_deleted,
    ticketing_signals.ticket_checked_in,
    ticketing_signals.tickets_sold,
    tourney_signals.tourney_started,
    tourney_signals.tourney_paused,
    tourney_signals.tourney_canceled,
    tourney_signals.tourney_finished,
    tourney_signals.match_ready,
    tourney_signals.match_reset,
    tourney_signals.match_score_submitted,
    tourney_signals.match_score_confirmed,
    tourney_signals.match_score_randomized,
    tourney_signals.participant_ready,
    tourney_signals.participant_eliminated,
    tourney_signals.participant_warned,
    tourney_signals.participant_disqualified,
    user_signals.account_created,
    user_signals.screen_name_changed,
    user_signals.email_address_invalidated,
    user_signals.details_updated,
    user_signals.account_suspended,
    user_signals.account_unsuspended,
    user_signals.account_deleted,
    user_badge_signals.user_badge_awarded,
]
for signal in SIGNALS:
    signal.connect(receive_signal)
