"""
byceps.blueprints.site.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ....services.board.transfer.models import CategoryWithLastUpdate
from ....services.user.transfer.models import User
from ....services.user_badge.transfer.models import Badge


@dataclass(frozen=True)
class CategoryWithLastUpdateAndUnseenFlag(CategoryWithLastUpdate):
    contains_unseen_postings: bool

    @classmethod
    def from_category_with_last_update(
        cls, category: CategoryWithLastUpdate, contains_unseen_postings: bool
    ) -> CategoryWithLastUpdateAndUnseenFlag:
        return cls(
            category.id,
            category.board_id,
            category.position,
            category.slug,
            category.title,
            category.description,
            category.topic_count,
            category.posting_count,
            category.hidden,
            category.last_posting_updated_at,
            category.last_posting_updated_by,
            contains_unseen_postings,
        )


@dataclass(frozen=True)
class Ticket:
    party_title: str


@dataclass(frozen=True)
class Creator(User):
    badges: set[Badge]
    ticket: Ticket

    @classmethod
    def from_(
        cls, user: User, badges: set[Badge], ticket: Optional[Ticket]
    ) -> Creator:
        return cls(
            user.id,
            user.screen_name,
            user.suspended,
            user.deleted,
            user.avatar_url,
            user.is_orga,
            badges,
            ticket,
        )
