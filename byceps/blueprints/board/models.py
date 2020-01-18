"""
byceps.blueprints.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import Optional, Set

from attr import attrs

from ...services.board.transfer.models import CategoryWithLastUpdate
from ...services.user.transfer.models import User
from ...services.user_badge.transfer.models import Badge


@attrs(auto_attribs=True, frozen=True, slots=True)
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


@attrs(auto_attribs=True, frozen=True, slots=True)
class Ticket:
    party_title: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class Creator(User):
    badges: Set[Badge]
    ticket: Ticket

    @classmethod
    def from_(
        cls, user: User, badges: Set[Badge], ticket: Optional[Ticket]
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
