"""
byceps.blueprints.api.v1.tourney.match.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from marshmallow import fields, Schema


class CreateMatchCommentRequest(Schema):
    match_id = fields.UUID(required=True)
    creator_id = fields.UUID(required=True)
    body = fields.Str(required=True)


class UpdateMatchCommentRequest(Schema):
    editor_id = fields.UUID(required=True)
    body = fields.Str(required=True)


class ModerateMatchCommentRequest(Schema):
    initiator_id = fields.UUID(required=True)
