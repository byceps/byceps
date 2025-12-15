"""
byceps.services.board.blueprints.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable, Sequence
from datetime import datetime

from flask import g

from byceps.services.authn.session.models import CurrentUser
from byceps.services.board import (
    board_access_control_service,
    board_posting_query_service,
    board_topic_query_service,
)
from byceps.services.board.dbmodels.posting import DbPosting
from byceps.services.board.dbmodels.topic import DbTopic
from byceps.services.board.models import BoardTopicCategory, BoardTopicSummary
from byceps.services.brand.models import BrandID
from byceps.services.orga_team import orga_team_service
from byceps.services.party import party_service
from byceps.services.party.models import Party, PartyID
from byceps.services.site import site_setting_service
from byceps.services.ticketing import ticket_service
from byceps.services.user import user_service
from byceps.services.user.models.user import UserID
from byceps.services.user_badge import user_badge_awarding_service
from byceps.services.user_badge.models import Badge
from byceps.util.authz import has_current_user_permission

from .models import Creator, Ticket


DEFAULT_POSTINGS_PER_PAGE = 10
DEFAULT_TOPICS_PER_PAGE = 10


def get_recent_topics(
    current_user: CurrentUser, *, limit=6
) -> Sequence[DbTopic] | None:
    """Return the most recently active board topics.

    Returns `None` if no board is configured for this site or the
    current user does not have access to the configured board.
    """
    board_id = g.site.board_id
    if board_id is None:
        return None

    has_access = board_access_control_service.has_user_access_to_board(
        current_user.id, board_id
    )
    if not has_access:
        return None

    include_hidden = may_current_user_view_hidden()
    topics = board_topic_query_service.get_recent_topics(
        board_id, limit=limit, include_hidden=include_hidden
    )

    add_topic_unseen_flag(topics, current_user)

    return topics


def to_topic_summaries(
    db_topics: Iterable[DbTopic], user: CurrentUser
) -> list[BoardTopicSummary]:
    """Build summary objects."""
    summaries = []

    for db_topic in db_topics:
        category = BoardTopicCategory(
            slug=db_topic.category.slug,
            title=db_topic.category.title,
        )

        contains_unseen_postings = _does_topic_contain_unseen_postings(
            db_topic, user
        )

        summary = BoardTopicSummary(
            id=db_topic.id,
            category=category,
            creator=db_topic.creator,
            title=db_topic.title,
            reply_count=db_topic.reply_count,
            last_updated_at=db_topic.last_updated_at,
            last_updated_by=db_topic.last_updated_by,
            hidden=db_topic.hidden,
            hidden_by=db_topic.hidden_by,
            locked=db_topic.locked,
            pinned=db_topic.pinned,
            posting_limited_to_moderators=db_topic.posting_limited_to_moderators,
            muted=db_topic.muted,
            contains_unseen_postings=contains_unseen_postings,
        )

        summaries.append(summary)

    return summaries


def add_topic_creators(db_topics: Iterable[DbTopic]) -> None:
    """Add each topic's creator as topic attribute."""
    creator_ids = {t.creator_id for t in db_topics}
    creators_by_id = user_service.get_users_indexed_by_id(
        creator_ids, include_avatars=True
    )

    for db_topic in db_topics:
        db_topic.creator = creators_by_id[db_topic.creator_id]


def add_topic_unseen_flag(
    db_topics: Iterable[DbTopic], user: CurrentUser
) -> None:
    """Add `unseen` flag to topics."""
    for db_topic in db_topics:
        db_topic.contains_unseen_postings = _does_topic_contain_unseen_postings(
            db_topic, user
        )


def _does_topic_contain_unseen_postings(
    db_topic: DbTopic, user: CurrentUser
) -> bool:
    """Return `True` if the topic contains postings yet unseen by the
    current user.
    """
    return (
        user.authenticated
        and board_topic_query_service.contains_topic_unseen_postings(
            db_topic, user.id
        )
    )


def add_unseen_flag_to_postings(
    db_postings: Iterable[DbPosting], last_viewed_at: datetime
) -> None:
    """Add the attribute 'unseen' to each post."""
    for db_posting in db_postings:
        db_posting.unseen = _is_posting_unseen(db_posting, last_viewed_at)


def _is_posting_unseen(db_posting: DbPosting, last_viewed_at: datetime) -> bool:
    """Return `True` if the posting has not yet been seen by the current
    user.
    """
    # Don't display any posting as new to a guest.
    if not g.user.authenticated:
        return False

    # Don't display the author's own posting as new to them.
    if db_posting.creator_id == g.user.id:
        return False

    return (last_viewed_at is None) or (db_posting.created_at > last_viewed_at)


def enrich_creators(
    db_postings: Iterable[DbPosting],
    brand_id: BrandID,
    party_id: PartyID | None,
) -> None:
    """Enrich creators with their orga status and badges."""
    creator_ids = {db_posting.creator_id for db_posting in db_postings}

    badges_by_user_id = _get_badges_for_users(creator_ids, brand_id)

    party: Party | None
    if party_id is not None:
        party = party_service.get_party(party_id)
        orga_ids = orga_team_service.select_orgas_for_party(
            creator_ids, party_id
        )
        ticket_users = ticket_service.select_ticket_users_for_party(
            creator_ids, party.id
        )
    else:
        party = None
        orga_ids = set()
        ticket_users = set()

    for db_posting in db_postings:
        user_id = db_posting.creator_id

        badges: set[Badge] = badges_by_user_id.get(user_id, set())

        ticket: Ticket | None
        if (party is not None) and (user_id in ticket_users):
            ticket = Ticket(party_title=party.title)
        else:
            ticket = None

        db_posting.creator = Creator.from_(
            db_posting.creator, orga_ids, badges, ticket
        )


def _get_badges_for_users(
    user_ids: set[UserID], brand_id: BrandID
) -> dict[UserID, set[Badge]]:
    """Fetch users' badges that are either global or belong to the brand."""
    badges_by_user_id = user_badge_awarding_service.get_badges_awarded_to_users(
        user_ids, featured_only=True
    )

    def generate_items():
        for user_id, badges in badges_by_user_id.items():
            selected_badges = {
                badge for badge in badges if badge.brand_id in {None, brand_id}
            }
            yield user_id, selected_badges

    return dict(generate_items())


def calculate_posting_page_number(db_posting: DbPosting) -> int:
    """Calculate the number of postings to show per page."""
    include_hidden = may_current_user_view_hidden()
    postings_per_page = get_postings_per_page_value()

    return board_posting_query_service.calculate_posting_page_number(
        db_posting, include_hidden, postings_per_page
    )


def get_topics_per_page_value() -> int:
    """Return the configured number of topics per page."""
    return _get_site_setting_int_value(
        'board_topics_per_page', DEFAULT_TOPICS_PER_PAGE
    )


def get_postings_per_page_value() -> int:
    """Return the configured number of postings per page."""
    return _get_site_setting_int_value(
        'board_postings_per_page', DEFAULT_POSTINGS_PER_PAGE
    )


def _get_site_setting_int_value(key, default_value) -> int:
    value = site_setting_service.find_setting_value(g.site.id, key)

    if value is None:
        return default_value

    return int(value)


def may_current_user_view_hidden() -> bool:
    """Return `True' if the current user may view hidden items."""
    return has_current_user_permission('board.view_hidden')


def may_topic_be_updated_by_current_user(db_topic: DbTopic) -> bool:
    """Return `True` if the topic may be updated by the current user."""
    return (
        not db_topic.locked
        and g.user.id == db_topic.creator_id
        and has_current_user_permission('board_topic.update')
    ) or has_current_user_permission('board.update_of_others')


def may_posting_be_updated_by_current_user(db_posting: DbPosting) -> bool:
    """Return `True` if the post may be updated by the current user."""
    return (
        not db_posting.topic.locked
        and g.user.id == db_posting.creator_id
        and has_current_user_permission('board_posting.update')
    ) or has_current_user_permission('board.update_of_others')
