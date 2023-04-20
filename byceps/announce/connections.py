"""
byceps.announce.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect event signals to announcement handlers.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Any, Optional

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
from ..events.page import PageCreated, PageDeleted, PageUpdated
from ..events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ..events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ..events.ticketing import TicketCheckedIn, TicketsSold
from ..events.tourney import (
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
from ..services.webhooks.models import OutgoingWebhook
from ..signals import auth as auth_signals
from ..signals import board as board_signals
from ..signals import guest_server as guest_server_signals
from ..signals import news as news_signals
from ..signals import page as page_signals
from ..signals import shop as shop_signals
from ..signals import snippet as snippet_signals
from ..signals import ticketing as ticketing_signals
from ..signals import tourney as tourney_signals
from ..signals import user as user_signals
from ..signals import user_badge as user_badge_signals
from ..util.jobqueue import enqueue, enqueue_at

from .handlers import (
    auth as auth_handlers,
    board as board_handlers,
    guest_server as guest_server_handlers,
    news as news_handlers,
    page as page_handlers,
    shop_order as shop_order_handlers,
    snippet as snippet_handlers,
    ticketing as ticketing_handlers,
    tourney as tourney_handlers,
    user as user_handlers,
    user_badge as user_badge_handlers,
)
from .helpers import (
    AnnouncementRequest,
    assemble_request_data,
    call_webhook,
    get_webhooks,
)


EVENT_TYPES_TO_HANDLERS = {
    UserLoggedIn: auth_handlers.announce_user_logged_in,
    BoardPostingCreated: board_handlers.announce_board_posting_created,
    BoardPostingHidden: board_handlers.announce_board_posting_hidden,
    BoardPostingUnhidden: board_handlers.announce_board_posting_unhidden,
    BoardTopicCreated: board_handlers.announce_board_topic_created,
    BoardTopicHidden: board_handlers.announce_board_topic_hidden,
    BoardTopicLocked: board_handlers.announce_board_topic_locked,
    BoardTopicMoved: board_handlers.announce_board_topic_moved,
    BoardTopicPinned: board_handlers.announce_board_topic_pinned,
    BoardTopicUnhidden: board_handlers.announce_board_topic_unhidden,
    BoardTopicUnlocked: board_handlers.announce_board_topic_unlocked,
    BoardTopicUnpinned: board_handlers.announce_board_topic_unpinned,
    GuestServerRegistered: guest_server_handlers.announce_guest_server_registered,
    NewsItemPublished: news_handlers.announce_news_item_published,
    PageCreated: page_handlers.announce_page_created,
    PageDeleted: page_handlers.announce_page_deleted,
    PageUpdated: page_handlers.announce_page_updated,
    ShopOrderCanceled: shop_order_handlers.announce_order_canceled,
    ShopOrderPaid: shop_order_handlers.announce_order_paid,
    ShopOrderPlaced: shop_order_handlers.announce_order_placed,
    SnippetCreated: snippet_handlers.announce_snippet_created,
    SnippetDeleted: snippet_handlers.announce_snippet_deleted,
    SnippetUpdated: snippet_handlers.announce_snippet_updated,
    TicketCheckedIn: ticketing_handlers.announce_ticket_checked_in,
    TicketsSold: ticketing_handlers.announce_tickets_sold,
    TourneyCanceled: tourney_handlers.announce_tourney_canceled,
    TourneyFinished: tourney_handlers.announce_tourney_finished,
    TourneyPaused: tourney_handlers.announce_tourney_paused,
    TourneyStarted: tourney_handlers.announce_tourney_started,
    TourneyMatchReady: tourney_handlers.announce_match_ready,
    TourneyMatchReset: tourney_handlers.announce_match_reset,
    TourneyMatchScoreConfirmed: tourney_handlers.announce_match_score_confirmed,
    TourneyMatchScoreRandomized: tourney_handlers.announce_match_score_randomized,
    TourneyMatchScoreSubmitted: tourney_handlers.announce_match_score_submitted,
    TourneyParticipantDisqualified: tourney_handlers.announce_participant_disqualified,
    TourneyParticipantEliminated: tourney_handlers.announce_participant_eliminated,
    TourneyParticipantReady: tourney_handlers.announce_participant_ready,
    TourneyParticipantWarned: tourney_handlers.announce_participant_warned,
    UserAccountCreated: user_handlers.announce_user_account_created,
    UserAccountDeleted: user_handlers.announce_user_account_deleted,
    UserAccountSuspended: user_handlers.announce_user_account_suspended,
    UserAccountUnsuspended: user_handlers.announce_user_account_unsuspended,
    UserBadgeAwarded: user_badge_handlers.announce_user_badge_awarded,
    UserDetailsUpdated: user_handlers.announce_user_details_updated,
    UserEmailAddressChanged: user_handlers.announce_user_email_address_changed,
    UserEmailAddressInvalidated: user_handlers.announce_user_email_address_invalidated,
    UserScreenNameChanged: user_handlers.announce_user_screen_name_changed,
}


def handle_event(event: _BaseEvent, webhook: OutgoingWebhook) -> None:
    announcement_request = build_announcement_request(event, webhook)
    if announcement_request is None:
        return

    announce(
        webhook, announcement_request.data, announcement_request.announce_at
    )


def build_announcement_request(
    event: _BaseEvent, webhook: OutgoingWebhook
) -> Optional[AnnouncementRequest]:
    event_type = type(event)

    handler = EVENT_TYPES_TO_HANDLERS.get(event_type)
    if handler is None:
        return None

    announcement = handler(event, webhook)
    if announcement is None:
        return None

    request_data = assemble_request_data(webhook, announcement.text)

    return AnnouncementRequest(request_data, announcement.announce_at)


def announce(
    webhook: OutgoingWebhook,
    request_data: dict[str, Any],
    announce_at: Optional[datetime],
) -> None:
    if announce_at is not None:
        # Schedule job to announce later.
        enqueue_at(announce_at, call_webhook, webhook, request_data)
    else:
        # Announce now.
        call_webhook(webhook, request_data)


def receive_signal(sender, *, event: Optional[_BaseEvent] = None) -> None:
    if event is None:
        return None

    webhooks = get_webhooks(event)
    for webhook in webhooks:
        enqueue(handle_event, event, webhook)


SIGNALS = [
    auth_signals.user_logged_in,
    board_signals.posting_created,
    board_signals.posting_hidden,
    board_signals.posting_unhidden,
    board_signals.topic_created,
    board_signals.topic_hidden,
    board_signals.topic_locked,
    board_signals.topic_moved,
    board_signals.topic_pinned,
    board_signals.topic_unhidden,
    board_signals.topic_unlocked,
    board_signals.topic_unpinned,
    guest_server_signals.guest_server_registered,
    news_signals.item_published,
    page_signals.page_created,
    page_signals.page_deleted,
    page_signals.page_updated,
    shop_signals.order_canceled,
    shop_signals.order_paid,
    shop_signals.order_placed,
    snippet_signals.snippet_created,
    snippet_signals.snippet_deleted,
    snippet_signals.snippet_updated,
    ticketing_signals.ticket_checked_in,
    ticketing_signals.tickets_sold,
    tourney_signals.tourney_canceled,
    tourney_signals.tourney_finished,
    tourney_signals.tourney_paused,
    tourney_signals.tourney_started,
    tourney_signals.match_ready,
    tourney_signals.match_reset,
    tourney_signals.match_score_confirmed,
    tourney_signals.match_score_randomized,
    tourney_signals.match_score_submitted,
    tourney_signals.participant_disqualified,
    tourney_signals.participant_eliminated,
    tourney_signals.participant_ready,
    tourney_signals.participant_warned,
    user_signals.account_created,
    user_signals.account_deleted,
    user_signals.account_suspended,
    user_signals.account_unsuspended,
    user_signals.details_updated,
    user_signals.email_address_changed,
    user_signals.email_address_invalidated,
    user_signals.screen_name_changed,
    user_badge_signals.user_badge_awarded,
]
for signal in SIGNALS:
    signal.connect(receive_signal)
