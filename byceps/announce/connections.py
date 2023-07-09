"""
byceps.announce.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect event signals to announcement handlers.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from typing import Callable, Optional

from blinker import NamedSignal

from byceps.events.auth import PasswordUpdatedEvent, UserLoggedInEvent
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
from byceps.services.webhooks.models import Announcement, OutgoingWebhook
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


AnnouncementEvent = type[_BaseEvent]
AnnouncementEventHandler = Callable[
    [str, _BaseEvent, OutgoingWebhook], Optional[Announcement]
]


class AnnouncementEventRegistry:
    def __init__(self) -> None:
        self._event_types_to_names: dict[AnnouncementEvent, str] = {}
        self._event_types_to_handlers: dict[
            AnnouncementEvent, AnnouncementEventHandler
        ] = {}

    def register_event(
        self,
        event: AnnouncementEvent,
        name: str,
        handler: AnnouncementEventHandler,
    ) -> None:
        self._event_types_to_names[event] = name
        self._event_types_to_handlers[event] = handler

    def get_event_name(self, event: _BaseEvent) -> str:
        event_type = type(event)
        return self._event_types_to_names[event_type]

    def get_event_names(self) -> set[str]:
        return set(self._event_types_to_names.values())

    def get_handler_for_event_type(
        self, event_type: AnnouncementEvent
    ) -> AnnouncementEventHandler | None:
        return self._event_types_to_handlers.get(event_type)


registry = AnnouncementEventRegistry()


for event, name, handler in [
    (
        PasswordUpdatedEvent,
        'password-updated',
        auth_handlers.announce_password_updated,
    ),
    (
        UserLoggedInEvent,
        'user-logged-in',
        auth_handlers.announce_user_logged_in,
    ),
    (
        BoardPostingCreatedEvent,
        'board-posting-created',
        board_handlers.announce_board_posting_created,
    ),
    (
        BoardPostingHiddenEvent,
        'board-posting-hidden',
        board_handlers.announce_board_posting_hidden,
    ),
    (
        BoardPostingUnhiddenEvent,
        'board-posting-unhidden',
        board_handlers.announce_board_posting_unhidden,
    ),
    (
        BoardTopicCreatedEvent,
        'board-topic-created',
        board_handlers.announce_board_topic_created,
    ),
    (
        BoardTopicHiddenEvent,
        'board-topic-hidden',
        board_handlers.announce_board_topic_hidden,
    ),
    (
        BoardTopicLockedEvent,
        'board-topic-locked',
        board_handlers.announce_board_topic_locked,
    ),
    (
        BoardTopicMovedEvent,
        'board-topic-moved',
        board_handlers.announce_board_topic_moved,
    ),
    (
        BoardTopicPinnedEvent,
        'board-topic-pinned',
        board_handlers.announce_board_topic_pinned,
    ),
    (
        BoardTopicUnhiddenEvent,
        'board-topic-unhidden',
        board_handlers.announce_board_topic_unhidden,
    ),
    (
        BoardTopicUnlockedEvent,
        'board-topic-unlocked',
        board_handlers.announce_board_topic_unlocked,
    ),
    (
        BoardTopicUnpinnedEvent,
        'board-topic-unpinned',
        board_handlers.announce_board_topic_unpinned,
    ),
    (
        GuestServerRegisteredEvent,
        'guest-server-registered',
        guest_server_handlers.announce_guest_server_registered,
    ),
    (
        NewsItemPublishedEvent,
        'news-item-published',
        news_handlers.announce_news_item_published,
    ),
    (PageCreatedEvent, 'page-created', page_handlers.announce_page_created),
    (PageDeletedEvent, 'page-deleted', page_handlers.announce_page_deleted),
    (PageUpdatedEvent, 'page-updated', page_handlers.announce_page_updated),
    (
        ShopOrderCanceledEvent,
        'shop-order-canceled',
        shop_order_handlers.announce_order_canceled,
    ),
    (
        ShopOrderPaidEvent,
        'shop-order-paid',
        shop_order_handlers.announce_order_paid,
    ),
    (
        ShopOrderPlacedEvent,
        'shop-order-placed',
        shop_order_handlers.announce_order_placed,
    ),
    (
        SnippetCreatedEvent,
        'snippet-created',
        snippet_handlers.announce_snippet_created,
    ),
    (
        SnippetDeletedEvent,
        'snippet-deleted',
        snippet_handlers.announce_snippet_deleted,
    ),
    (
        SnippetUpdatedEvent,
        'snippet-updated',
        snippet_handlers.announce_snippet_updated,
    ),
    (
        TicketCheckedInEvent,
        'ticket-checked-in',
        ticketing_handlers.announce_ticket_checked_in,
    ),
    (
        TicketsSoldEvent,
        'tickets-sold',
        ticketing_handlers.announce_tickets_sold,
    ),
    (
        TourneyCanceledEvent,
        'tourney-canceled',
        tourney_handlers.announce_tourney_canceled,
    ),
    (
        TourneyFinishedEvent,
        'tourney-finished',
        tourney_handlers.announce_tourney_finished,
    ),
    (
        TourneyPausedEvent,
        'tourney-paused',
        tourney_handlers.announce_tourney_paused,
    ),
    (
        TourneyStartedEvent,
        'tourney-started',
        tourney_handlers.announce_tourney_started,
    ),
    (
        TourneyMatchReadyEvent,
        'tourney-match-ready',
        tourney_handlers.announce_match_ready,
    ),
    (
        TourneyMatchResetEvent,
        'tourney-match-reset',
        tourney_handlers.announce_match_reset,
    ),
    (
        TourneyMatchScoreConfirmedEvent,
        'tourney-match-score-confirmed',
        tourney_handlers.announce_match_score_confirmed,
    ),
    (
        TourneyMatchScoreRandomizedEvent,
        'tourney-match-score-randomized',
        tourney_handlers.announce_match_score_randomized,
    ),
    (
        TourneyMatchScoreSubmittedEvent,
        'tourney-match-score-submitted',
        tourney_handlers.announce_match_score_submitted,
    ),
    (
        TourneyParticipantDisqualifiedEvent,
        'tourney-participant-disqualified',
        tourney_handlers.announce_participant_disqualified,
    ),
    (
        TourneyParticipantEliminatedEvent,
        'tourney-participant-eliminated',
        tourney_handlers.announce_participant_eliminated,
    ),
    (
        TourneyParticipantReadyEvent,
        'tourney-participant-ready',
        tourney_handlers.announce_participant_ready,
    ),
    (
        TourneyParticipantWarnedEvent,
        'tourney-participant-warned',
        tourney_handlers.announce_participant_warned,
    ),
    (
        UserAccountCreatedEvent,
        'user-account-created',
        user_handlers.announce_user_account_created,
    ),
    (
        UserAccountDeletedEvent,
        'user-account-deleted',
        user_handlers.announce_user_account_deleted,
    ),
    (
        UserAccountSuspendedEvent,
        'user-account-suspended',
        user_handlers.announce_user_account_suspended,
    ),
    (
        UserAccountUnsuspendedEvent,
        'user-account-unsuspended',
        user_handlers.announce_user_account_unsuspended,
    ),
    (
        UserBadgeAwardedEvent,
        'user-badge-awarded',
        user_badge_handlers.announce_user_badge_awarded,
    ),
    (
        UserDetailsUpdatedEvent,
        'user-details-updated',
        user_handlers.announce_user_details_updated,
    ),
    (
        UserEmailAddressChangedEvent,
        'user-email-address-changed',
        user_handlers.announce_user_email_address_changed,
    ),
    (
        UserEmailAddressInvalidatedEvent,
        'user-email-address-invalidated',
        user_handlers.announce_user_email_address_invalidated,
    ),
    (
        UserScreenNameChangedEvent,
        'user-screen-name-changed',
        user_handlers.announce_user_screen_name_changed,
    ),
]:
    registry.register_event(event, name, handler)


_SIGNALS: list[NamedSignal] = [
    auth_signals.password_updated,
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


def get_signals():
    return _SIGNALS
