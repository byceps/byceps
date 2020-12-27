"""
byceps.announce.irc.connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.board import (
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
from ...events.news import NewsItemPublished
from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...events.tourney import (
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
from ...events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from ...events.user_badge import UserBadgeAwarded
from ...signals import board as board_signals
from ...signals import news as news_signals
from ...signals import shop as shop_signals
from ...signals import snippet as snippet_signals
from ...signals import ticketing as ticketing_signals
from ...signals import tourney as tourney_signals
from ...signals import user as user_signals
from ...signals import user_badge as user_badge_signals
from ...util.jobqueue import enqueue

from . import (
    board,
    news,
    shop_order,
    snippet,
    ticketing,
    tourney,
    user,
    user_badge,
)


# board topics


@board_signals.topic_created.connect
def _on_board_topic_created(
    sender, *, event: Optional[BoardTopicCreated] = None
) -> None:
    enqueue(board.announce_board_topic_created, event)


@board_signals.topic_hidden.connect
def _on_board_topic_hidden(
    sender, *, event: Optional[BoardTopicHidden] = None
) -> None:
    enqueue(board.announce_board_topic_hidden, event)


@board_signals.topic_unhidden.connect
def _on_board_topic_unhidden(
    sender, *, event: Optional[BoardTopicUnhidden] = None
) -> None:
    enqueue(board.announce_board_topic_unhidden, event)


@board_signals.topic_locked.connect
def _on_board_topic_locked(
    sender, *, event: Optional[BoardTopicLocked] = None
) -> None:
    enqueue(board.announce_board_topic_locked, event)


@board_signals.topic_unlocked.connect
def _on_board_topic_unlocked(
    sender, *, event: Optional[BoardTopicUnlocked] = None
) -> None:
    enqueue(board.announce_board_topic_unlocked, event)


@board_signals.topic_pinned.connect
def _on_board_topic_pinned(
    sender, *, event: Optional[BoardTopicPinned] = None
) -> None:
    enqueue(board.announce_board_topic_pinned, event)


@board_signals.topic_unpinned.connect
def _on_board_topic_unpinned(
    sender, *, event: Optional[BoardTopicUnpinned] = None
) -> None:
    enqueue(board.announce_board_topic_unpinned, event)


@board_signals.topic_moved.connect
def _on_board_topic_moved(
    sender, *, event: Optional[BoardTopicMoved] = None
) -> None:
    enqueue(board.announce_board_topic_moved, event)


# board postings


@board_signals.posting_created.connect
def _on_board_posting_created(
    sender, *, event: Optional[BoardPostingCreated] = None
) -> None:
    enqueue(board.announce_board_posting_created, event)


@board_signals.posting_hidden.connect
def _on_board_posting_hidden(
    sender, *, event: Optional[BoardPostingHidden] = None
) -> None:
    enqueue(board.announce_board_posting_hidden, event)


@board_signals.posting_unhidden.connect
def _on_board_posting_unhidden(
    sender, *, event: Optional[BoardPostingUnhidden] = None
) -> None:
    enqueue(board.announce_board_posting_unhidden, event)


# news


@news_signals.item_published.connect
def _on_news_item_published(
    sender, *, event: Optional[NewsItemPublished] = None
) -> None:
    enqueue(news.announce_news_item_published, event)


# shop orders


@shop_signals.order_placed.connect
def _on_order_placed(
    sender, *, event: Optional[ShopOrderPlaced] = None
) -> None:
    enqueue(shop_order.announce_order_placed, event)


@shop_signals.order_paid.connect
def _on_order_paid(sender, *, event: Optional[ShopOrderPaid] = None) -> None:
    enqueue(shop_order.announce_order_paid, event)


@shop_signals.order_canceled.connect
def _on_order_canceled(
    sender, *, event: Optional[ShopOrderCanceled] = None
) -> None:
    enqueue(shop_order.announce_order_canceled, event)


# snippets


@snippet_signals.snippet_created.connect
def _on_snippet_created(
    sender, *, event: Optional[SnippetCreated] = None
) -> None:
    enqueue(snippet.announce_snippet_created, event)


@snippet_signals.snippet_updated.connect
def _on_snippet_updated(
    sender, *, event: Optional[SnippetUpdated] = None
) -> None:
    enqueue(snippet.announce_snippet_updated, event)


@snippet_signals.snippet_deleted.connect
def _on_snippet_deleted(
    sender, *, event: Optional[SnippetDeleted] = None
) -> None:
    enqueue(snippet.announce_snippet_deleted, event)


# ticketing


@ticketing_signals.ticket_checked_in.connect
def _on_ticket_checked_in(
    sender, *, event: Optional[TicketCheckedIn] = None
) -> None:
    enqueue(ticketing.announce_ticket_checked_in, event)


@ticketing_signals.tickets_sold.connect
def _on_tickets_sold(sender, *, event: Optional[TicketsSold] = None) -> None:
    enqueue(ticketing.announce_tickets_sold, event)


# tourneys


@tourney_signals.tourney_started.connect
def _on_tourney_started(sender, *, event: Optional[TourneyStarted] = None):
    enqueue(tourney.announce_tourney_started, event)


@tourney_signals.tourney_paused.connect
def _on_tourney_paused(sender, *, event: Optional[TourneyPaused] = None):
    enqueue(tourney.announce_tourney_paused, event)


@tourney_signals.tourney_canceled.connect
def _on_tourney_canceled(sender, *, event: Optional[TourneyCanceled] = None):
    enqueue(tourney.announce_tourney_canceled, event)


@tourney_signals.tourney_finished.connect
def _on_tourney_finished(sender, *, event: Optional[TourneyFinished] = None):
    enqueue(tourney.announce_tourney_finished, event)


# tourney matches


@tourney_signals.match_ready.connect
def _on_match_ready(sender, *, event: Optional[TourneyMatchReady] = None):
    enqueue(tourney.announce_match_ready, event)


@tourney_signals.match_reset.connect
def _on_match_reset(sender, *, event: Optional[TourneyMatchReset] = None):
    enqueue(tourney.announce_match_reset, event)


@tourney_signals.match_score_submitted.connect
def _on_match_score_submitted(
    sender, *, event: Optional[TourneyMatchScoreSubmitted] = None
):
    enqueue(tourney.announce_match_score_submitted, event)


@tourney_signals.match_score_confirmed.connect
def _on_match_score_confirmed(
    sender, *, event: Optional[TourneyMatchScoreConfirmed] = None
):
    enqueue(tourney.announce_match_score_confirmed, event)


@tourney_signals.match_score_randomized.connect
def _on_match_score_randomized(
    sender, *, event: Optional[TourneyMatchScoreRandomized] = None
):
    enqueue(tourney.announce_match_score_randomized, event)


# tourney participants


@tourney_signals.participant_ready.connect
def _on_participant_ready(
    sender, *, event: Optional[TourneyParticipantReady] = None
):
    enqueue(tourney.announce_participant_ready, event)


@tourney_signals.participant_eliminated.connect
def _on_participant_eliminated(
    sender, *, event: Optional[TourneyParticipantEliminated] = None
):
    enqueue(tourney.announce_participant_eliminated, event)


@tourney_signals.participant_warned.connect
def _on_participant_warned(
    sender, *, event: Optional[TourneyParticipantWarned] = None
):
    enqueue(tourney.announce_participant_warned, event)


@tourney_signals.participant_disqualified.connect
def _on_participant_disqualified(
    sender, *, event: Optional[TourneyParticipantDisqualified] = None
):
    enqueue(tourney.announce_participant_disqualified, event)


# users


@user_signals.account_created.connect
def _on_user_account_created(
    sender, *, event: Optional[UserAccountCreated] = None
) -> None:
    enqueue(user.announce_user_account_created, event)


@user_signals.screen_name_changed.connect
def _on_user_screen_name_changed(
    sender, *, event: Optional[UserScreenNameChanged] = None
) -> None:
    enqueue(user.announce_user_screen_name_changed, event)


@user_signals.email_address_invalidated.connect
def _on_user_email_address_invalidated(
    sender, *, event: Optional[UserEmailAddressInvalidated] = None
) -> None:
    enqueue(user.announce_user_email_address_invalidated, event)


@user_signals.details_updated.connect
def _on_user_details_updated_changed(
    sender, *, event: Optional[UserDetailsUpdated] = None
) -> None:
    enqueue(user.announce_user_details_updated_changed, event)


@user_signals.account_suspended.connect
def _on_user_account_suspended(
    sender, *, event: Optional[UserAccountSuspended] = None
) -> None:
    enqueue(user.announce_user_account_suspended, event)


@user_signals.account_unsuspended.connect
def _on_user_account_unsuspended(
    sender, *, event: Optional[UserAccountUnsuspended] = None
) -> None:
    enqueue(user.announce_user_account_unsuspended, event)


@user_signals.account_deleted.connect
def _on_user_account_deleted(
    sender, *, event: Optional[UserAccountDeleted] = None
) -> None:
    enqueue(user.announce_user_account_deleted, event)


# user badges


@user_badge_signals.user_badge_awarded.connect
def _on_user_badge_awarded(
    sender, *, event: Optional[UserBadgeAwarded] = None
) -> None:
    enqueue(user_badge.announce_user_badge_awarded, event)
