"""
byceps.services.board.board_posting_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select

from byceps.database import db, paginate, Pagination
from byceps.services.user import user_service
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.iterables import index_of

from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbPosting, DbPostingReaction
from .dbmodels.topic import DbTopic
from .models import BoardID, PostingID, PostingReactionUser, TopicID


def count_postings_for_board(board_id: BoardID) -> int:
    """Return the number of postings for that board."""
    return (
        db.session.scalar(
            select(db.func.count(DbPosting.id))
            .join(DbTopic)
            .join(DbBoardCategory)
            .filter(DbBoardCategory.board_id == board_id)
        )
        or 0
    )


def find_db_posting(posting_id: PostingID) -> DbPosting | None:
    """Return the posting with that id, or `None` if not found."""
    return db.session.get(DbPosting, posting_id)


def get_db_posting(posting_id: PostingID) -> DbPosting:
    """Return the posting with that id."""
    db_posting = find_db_posting(posting_id)

    if db_posting is None:
        raise ValueError(f'Unknown posting ID "{posting_id}"')

    return db_posting


def paginate_postings(
    topic_id: TopicID,
    include_hidden: bool,
    page: int,
    per_page: int,
) -> Pagination:
    """Paginate postings in that topic, as visible for the user."""
    stmt = (
        select(DbPosting)
        .options(
            db.joinedload(DbPosting.topic),
            db.joinedload(DbPosting.last_edited_by).load_only(
                DbUser.screen_name
            ),
            db.joinedload(DbPosting.hidden_by).load_only(DbUser.screen_name),
            db.joinedload(DbPosting.reactions)
            .joinedload(DbPostingReaction.user)
            .load_only(DbUser.id, DbUser.screen_name),
        )
        .filter_by(topic_id=topic_id)
        .order_by(DbPosting.created_at.asc())
    )

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    db_postings = paginate(stmt, page, per_page)

    creator_ids = {db_posting.creator_id for db_posting in db_postings.items}
    creators_by_id = user_service.get_users_indexed_by_id(
        creator_ids, include_avatars=True
    )

    for db_posting in db_postings.items:
        db_posting.creator = creators_by_id[db_posting.creator_id]
        db_posting.reactions_by_kind = _get_reactions_by_kind(
            db_posting.reactions
        )

    return db_postings


def _get_reactions_by_kind(
    db_reactions: list[DbPostingReaction],
) -> dict[str, list[PostingReactionUser]]:
    reactions_by_kind = defaultdict(list)

    for db_reaction in db_reactions:
        reactions_by_kind[db_reaction.kind].append(
            PostingReactionUser(
                id=db_reaction.user.id,
                screen_name=db_reaction.user.screen_name,
            )
        )

    return dict(reactions_by_kind)


def calculate_posting_page_number(
    db_posting: DbPosting, include_hidden: bool, postings_per_page: int
) -> int:
    """Return the number of the page the posting should appear on."""
    stmt = select(DbPosting).filter_by(topic_id=db_posting.topic_id)

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    stmt = stmt.order_by(DbPosting.created_at.asc())

    db_topic_postings = db.session.scalars(stmt).all()

    index = index_of(db_topic_postings, lambda p: p == db_posting)
    if index is None:
        return 1  # Shouldn't happen.

    return divmod(index, postings_per_page)[0] + 1
