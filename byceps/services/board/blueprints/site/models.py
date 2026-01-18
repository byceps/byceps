"""
byceps.services.board.blueprints.site.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Self

from byceps.services.board.models import ReactionKind
from byceps.services.user.models.user import User, UserID
from byceps.services.user_badge.models import Badge


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
            avatar_url=user.avatar_url,
            is_orga=user.id in orga_ids,
            badges=badges,
            ticket=ticket,
        )


@dataclass(frozen=True, kw_only=True)
class ReactionKindEmojiSymbol:
    value: str

    @property
    def type_(self) -> str:
        return 'emoji'


@dataclass(frozen=True, kw_only=True)
class ReactionKindImageSymbol:
    filename: str

    @property
    def type_(self) -> str:
        return 'image'


ReactionKindSymbol = ReactionKindEmojiSymbol | ReactionKindImageSymbol


@dataclass(frozen=True, kw_only=True)
class ReactionKindPresentation:
    kind: ReactionKind
    symbol: ReactionKindSymbol


def build_reaction_kind_presentation(
    kind_str: str, *, emoji: str | None = None, image: str | None = None
) -> ReactionKindPresentation:
    kind = ReactionKind(kind_str)
    symbol: ReactionKindSymbol

    if emoji and image:
        raise ValueError('Either emoji or image must be specified, not both')
    elif emoji:
        symbol = ReactionKindEmojiSymbol(value=emoji)
    elif image:
        symbol = ReactionKindImageSymbol(filename=image)
    else:
        raise ValueError('Either emoji or image must be specified')

    return ReactionKindPresentation(kind=kind, symbol=symbol)
