"""
byceps.announce.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect event signals to announcement handlers.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable

from blinker import NamedSignal

from byceps.services.authn import signals as authn_signals
from byceps.services.authn.events import PasswordUpdatedEvent, UserLoggedInEvent
from byceps.services.authz import signals as authz_signals
from byceps.services.authz.events import (
    RoleAssignedToUserEvent,
    RoleDeassignedFromUserEvent,
)
from byceps.services.board import signals as board_signals
from byceps.services.board.events import (
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
from byceps.services.core.events import _BaseEvent
from byceps.services.external_accounts import (
    signals as external_accounts_signals,
)
from byceps.services.external_accounts.events import (
    ExternalAccountConnectedEvent,
    ExternalAccountDisconnectedEvent,
)
from byceps.services.guest_server import signals as guest_server_signals
from byceps.services.guest_server.events import (
    GuestServerApprovedEvent,
    GuestServerCheckedInEvent,
    GuestServerCheckedOutEvent,
    GuestServerRegisteredEvent,
)
from byceps.services.news import signals as news_signals
from byceps.services.news.events import NewsItemPublishedEvent
from byceps.services.newsletter import signals as newsletter_signals
from byceps.services.newsletter.events import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from byceps.services.orga import signals as orga_signals
from byceps.services.orga.events import (
    OrgaStatusGrantedEvent,
    OrgaStatusRevokedEvent,
)
from byceps.services.page import signals as page_signals
from byceps.services.page.events import (
    PageCreatedEvent,
    PageDeletedEvent,
    PageUpdatedEvent,
)
from byceps.services.shop.order import signals as shop_order_signals
from byceps.services.shop.order.events import (
    ShopOrderCanceledEvent,
    ShopOrderPaidEvent,
    ShopOrderPlacedEvent,
)
from byceps.services.snippet import signals as snippet_signals
from byceps.services.snippet.events import (
    SnippetCreatedEvent,
    SnippetDeletedEvent,
    SnippetUpdatedEvent,
)
from byceps.services.ticketing import signals as ticketing_signals
from byceps.services.ticketing.events import (
    TicketCheckedInEvent,
    TicketsSoldEvent,
)
from byceps.services.tourney import signals as tourney_signals
from byceps.services.tourney.events import (
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
from byceps.services.user.events import (
    UserAccountCreatedEvent,
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserEmailAddressInvalidatedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.user_badge.events import UserBadgeAwardedEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook
from byceps.signals import (
    user as user_signals,
    user_badge as user_badge_signals,
)

from .handlers import (
    authn as authn_handlers,
    authz as authz_handlers,
    board as board_handlers,
    external_accounts as external_accounts_handlers,
    guest_server as guest_server_handlers,
    news as news_handlers,
    newsletter as newsletter_handler,
    orga as orga_handlers,
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
    [str, _BaseEvent, OutgoingWebhook], Announcement | None
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
        authn_handlers.announce_password_updated,
    ),
    (
        UserLoggedInEvent,
        'user-logged-in',
        authn_handlers.announce_user_logged_in,
    ),
    (
        RoleAssignedToUserEvent,
        'role-assigned-to-user',
        authz_handlers.announce_role_assigned_to_user,
    ),
    (
        RoleDeassignedFromUserEvent,
        'role-deassigned-from-user',
        authz_handlers.announce_role_deassigned_from_user,
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
        ExternalAccountConnectedEvent,
        'external-account-connected',
        external_accounts_handlers.announce_external_account_connected,
    ),
    (
        ExternalAccountDisconnectedEvent,
        'external-account-disconnected',
        external_accounts_handlers.announce_external_account_disconnected,
    ),
    (
        GuestServerApprovedEvent,
        'guest-server-approved',
        guest_server_handlers.announce_guest_server_approved,
    ),
    (
        GuestServerCheckedInEvent,
        'guest-server-checked-in',
        guest_server_handlers.announce_guest_server_checked_in,
    ),
    (
        GuestServerCheckedOutEvent,
        'guest-server-checked-out',
        guest_server_handlers.announce_guest_server_checked_out,
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
    (
        SubscribedToNewsletterEvent,
        'newsletter-subscribed',
        newsletter_handler.announce_subscribed_to_newsletter,
    ),
    (
        UnsubscribedFromNewsletterEvent,
        'newsletter-unsubscribed',
        newsletter_handler.announce_unsubscribed_from_newsletter,
    ),
    (
        OrgaStatusGrantedEvent,
        'orga-status-granted',
        orga_handlers.announce_orga_status_granted,
    ),
    (
        OrgaStatusRevokedEvent,
        'orga-status-revoked',
        orga_handlers.announce_orga_status_revoked,
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
    authn_signals.password_updated,
    authn_signals.user_logged_in,
    authz_signals.role_assigned_to_user,
    authz_signals.role_deassigned_from_user,
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
    external_accounts_signals.external_account_connected,
    external_accounts_signals.external_account_disconnected,
    guest_server_signals.guest_server_approved,
    guest_server_signals.guest_server_checked_in,
    guest_server_signals.guest_server_checked_out,
    guest_server_signals.guest_server_registered,
    news_signals.item_published,
    newsletter_signals.newsletter_subscribed,
    newsletter_signals.newsletter_unsubscribed,
    orga_signals.orga_status_granted,
    orga_signals.orga_status_revoked,
    page_signals.page_created,
    page_signals.page_deleted,
    page_signals.page_updated,
    shop_order_signals.order_canceled,
    shop_order_signals.order_paid,
    shop_order_signals.order_placed,
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
