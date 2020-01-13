"""
byceps.blueprints.api.tourney.match.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from marshmallow import fields, Schema


class CreateMatchCommentRequest(Schema):
    match_id = fields.UUID()
    creator_id = fields.UUID()
    body = fields.Str()


class UpdateMatchCommentRequest(Schema):
    editor_id = fields.UUID()
    body = fields.Str()


class ModerateMatchCommentRequest(Schema):
    initiator_id = fields.UUID()
