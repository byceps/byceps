"""
byceps.blueprints.api.v1.tourney.match.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pydantic import BaseModel


class CreateMatchCommentRequest(BaseModel):
    match_id: UUID
    creator_id: UUID
    body: str


class UpdateMatchCommentRequest(BaseModel):
    editor_id: UUID
    body: str


class ModerateMatchCommentRequest(BaseModel):
    initiator_id: UUID
