"""
byceps.announce.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect event signals to announcement handlers.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

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
from byceps.events.user_badge import UserBadgeAwardedEvent
from byceps.services.webhooks.models import AnnouncementRequest, OutgoingWebhook
from byceps.signals import (
    auth as auth_signals,
    board as board_signals,
    guest_server as guest_server_signals,
    news as news_signals,
    page as page_signals,
    shop as shop_signals,
    snippet as snippet_signals,
    ticketing as ticketing_signals,
    tourney as tourney_signals,
    user as user_signals,
    user_badge as user_badge_signals,
)
from byceps.util.jobqueue import enqueue

from .announce import announce, assemble_announcement_request, get_webhooks


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
    UserBadgeAwardedEvent: 'user-badge-awarded',
    UserDetailsUpdatedEvent: 'user-details-updated',
    UserEmailAddressChangedEvent: 'user-email-address-changed',
    UserEmailAddressInvalidatedEvent: 'user-email-address-invalidated',
    UserScreenNameChangedEvent: 'user-screen-name-changed',
}


_EVENT_TYPES_TO_HANDLERS = {}


def register_handlers() -> None:
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

    global _EVENT_TYPES_TO_HANDLERS
    _EVENT_TYPES_TO_HANDLERS = {
        UserLoggedInEvent: auth_handlers.announce_user_logged_in,
        BoardPostingCreatedEvent: board_handlers.announce_board_posting_created,
        BoardPostingHiddenEvent: board_handlers.announce_board_posting_hidden,
        BoardPostingUnhiddenEvent: board_handlers.announce_board_posting_unhidden,
        BoardTopicCreatedEvent: board_handlers.announce_board_topic_created,
        BoardTopicHiddenEvent: board_handlers.announce_board_topic_hidden,
        BoardTopicLockedEvent: board_handlers.announce_board_topic_locked,
        BoardTopicMovedEvent: board_handlers.announce_board_topic_moved,
        BoardTopicPinnedEvent: board_handlers.announce_board_topic_pinned,
        BoardTopicUnhiddenEvent: board_handlers.announce_board_topic_unhidden,
        BoardTopicUnlockedEvent: board_handlers.announce_board_topic_unlocked,
        BoardTopicUnpinnedEvent: board_handlers.announce_board_topic_unpinned,
        GuestServerRegisteredEvent: guest_server_handlers.announce_guest_server_registered,
        NewsItemPublishedEvent: news_handlers.announce_news_item_published,
        PageCreatedEvent: page_handlers.announce_page_created,
        PageDeletedEvent: page_handlers.announce_page_deleted,
        PageUpdatedEvent: page_handlers.announce_page_updated,
        ShopOrderCanceledEvent: shop_order_handlers.announce_order_canceled,
        ShopOrderPaidEvent: shop_order_handlers.announce_order_paid,
        ShopOrderPlacedEvent: shop_order_handlers.announce_order_placed,
        SnippetCreatedEvent: snippet_handlers.announce_snippet_created,
        SnippetDeletedEvent: snippet_handlers.announce_snippet_deleted,
        SnippetUpdatedEvent: snippet_handlers.announce_snippet_updated,
        TicketCheckedInEvent: ticketing_handlers.announce_ticket_checked_in,
        TicketsSoldEvent: ticketing_handlers.announce_tickets_sold,
        TourneyCanceledEvent: tourney_handlers.announce_tourney_canceled,
        TourneyFinishedEvent: tourney_handlers.announce_tourney_finished,
        TourneyPausedEvent: tourney_handlers.announce_tourney_paused,
        TourneyStartedEvent: tourney_handlers.announce_tourney_started,
        TourneyMatchReadyEvent: tourney_handlers.announce_match_ready,
        TourneyMatchResetEvent: tourney_handlers.announce_match_reset,
        TourneyMatchScoreConfirmedEvent: tourney_handlers.announce_match_score_confirmed,
        TourneyMatchScoreRandomizedEvent: tourney_handlers.announce_match_score_randomized,
        TourneyMatchScoreSubmittedEvent: tourney_handlers.announce_match_score_submitted,
        TourneyParticipantDisqualifiedEvent: tourney_handlers.announce_participant_disqualified,
        TourneyParticipantEliminatedEvent: tourney_handlers.announce_participant_eliminated,
        TourneyParticipantReadyEvent: tourney_handlers.announce_participant_ready,
        TourneyParticipantWarnedEvent: tourney_handlers.announce_participant_warned,
        UserAccountCreatedEvent: user_handlers.announce_user_account_created,
        UserAccountDeletedEvent: user_handlers.announce_user_account_deleted,
        UserAccountSuspendedEvent: user_handlers.announce_user_account_suspended,
        UserAccountUnsuspendedEvent: user_handlers.announce_user_account_unsuspended,
        UserBadgeAwardedEvent: user_badge_handlers.announce_user_badge_awarded,
        UserDetailsUpdatedEvent: user_handlers.announce_user_details_updated,
        UserEmailAddressChangedEvent: user_handlers.announce_user_email_address_changed,
        UserEmailAddressInvalidatedEvent: user_handlers.announce_user_email_address_invalidated,
        UserScreenNameChangedEvent: user_handlers.announce_user_screen_name_changed,
    }


def get_name_for_event(event: _BaseEvent) -> str:
    """Return the name for the event type.

    Raise exception if no name is defined for the event type.
    """
    event_type = type(event)
    return EVENT_TYPES_TO_NAMES[event_type]


def handle_event(event: _BaseEvent, webhook: OutgoingWebhook) -> None:
    announcement_request = build_announcement_request(event, webhook)
    if announcement_request is None:
        return

    announce(announcement_request)


def build_announcement_request(
    event: _BaseEvent, webhook: OutgoingWebhook
) -> AnnouncementRequest | None:
    event_type = type(event)

    handler = _EVENT_TYPES_TO_HANDLERS.get(event_type)
    if handler is None:
        return None

    announcement = handler(event, webhook)
    if announcement is None:
        return None

    return assemble_announcement_request(
        webhook, announcement.text, announce_at=announcement.announce_at
    )


def receive_signal(sender, *, event: _BaseEvent | None = None) -> None:
    if event is None:
        return None

    event_name = get_name_for_event(event)
    webhooks = get_webhooks(event_name)
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


def enable_announcements() -> None:
    register_handlers()

    for signal in SIGNALS:
        signal.connect(receive_signal)
