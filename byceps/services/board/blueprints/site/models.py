"""
byceps.services.board.blueprints.site.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Self

from byceps.services.board.models import BoardCategoryWithLastUpdate
from byceps.services.user.models.user import User, UserID
from byceps.services.user_badge.models import Badge


@dataclass(frozen=True, kw_only=True)
class CategoryWithLastUpdateAndUnseenFlag(BoardCategoryWithLastUpdate):
    contains_unseen_postings: bool

    @classmethod
    def from_category_with_last_update(
        cls,
        category: BoardCategoryWithLastUpdate,
        contains_unseen_postings: bool,
    ) -> Self:
        return cls(
            id=category.id,
            board_id=category.board_id,
            position=category.position,
            slug=category.slug,
            title=category.title,
            description=category.description,
            topic_count=category.topic_count,
            posting_count=category.posting_count,
            hidden=category.hidden,
            last_posting_updated_at=category.last_posting_updated_at,
            last_posting_updated_by=category.last_posting_updated_by,
            contains_unseen_postings=contains_unseen_postings,
        )


@dataclass(frozen=True, kw_only=True)
class Ticket:
    party_title: str


@dataclass(frozen=True, kw_only=True)
class Creator(User):
    is_orga: bool
    badges: set[Badge]
    ticket: Ticket | None

    @classmethod
    def from_(
        cls,
        user: User,
        orga_ids: set[UserID],
        badges: set[Badge],
        ticket: Ticket | None,
    ) -> Self:
        return cls(
            id=user.id,
            screen_name=user.screen_name,
            initialized=user.initialized,
            suspended=user.suspended,
            deleted=user.deleted,
            locale=user.locale,
            avatar_url=user.avatar_url,
            is_orga=user.id in orga_ids,
            badges=badges,
            ticket=ticket,
        )
