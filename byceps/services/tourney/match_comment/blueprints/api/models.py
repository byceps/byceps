"""
byceps.services.tourney.match_comment.blueprints.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class CreateMatchCommentRequest:
    match_id: UUID
    creator_id: UUID
    body: str


@dataclass(frozen=True, kw_only=True)
class UpdateMatchCommentRequest:
    editor_id: UUID
    body: str


@dataclass(frozen=True, kw_only=True)
class ModerateMatchCommentRequest:
    initiator_id: UUID
