"""
byceps.blueprints.api.v1.tourney.match.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from flask import abort, jsonify, request, url_for
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta

from .......services.tourney import (
    match_comment_service as comment_service,
    match_service,
)
from .......services.tourney.transfer.models import (
    Match,
    MatchID,
    MatchComment,
    MatchCommentID,
)
from .......services.user import service as user_service
from .......services.user.transfer.models import User
from .......signals import tourney as tourney_signals
from .......util.framework.blueprint import create_blueprint
from .......util.views import respond_created, respond_no_content

from .....decorators import api_token_required

from .schemas import (
    CreateMatchCommentRequest,
    ModerateMatchCommentRequest,
    UpdateMatchCommentRequest,
)


blueprint = create_blueprint('tourney_match_comments', __name__)


@blueprint.get('/match_comments/<uuid:comment_id>')
@api_token_required
def get_comment(comment_id):
    """Return the comment."""
    comment = _get_comment_or_404(comment_id)

    comment_dto = _comment_to_json(comment)

    return jsonify(comment_dto)


@blueprint.get('/matches/<uuid:match_id>/comments')
@api_token_required
def get_comments_for_match(match_id):
    """Return the comments on the match."""
    match = _get_match_or_404(match_id)

    party_id = request.args.get('party_id')

    comments = comment_service.get_comments(
        match.id, party_id=party_id, include_hidden=True
    )

    comment_dtos = list(map(_comment_to_json, comments))

    return jsonify(
        {
            'comments': comment_dtos,
        }
    )


def _comment_to_json(comment: MatchComment) -> dict[str, Any]:
    creator = comment.created_by
    last_editor = comment.last_edited_by
    moderator = comment.hidden_by

    return {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': _user_to_json(creator),
        'body_text': comment.body_text,
        'body_html': comment.body_html,
        'last_edited_at': _potential_datetime_to_json(comment.last_edited_at),
        'last_editor': _potential_user_to_json(last_editor),
        'hidden': comment.hidden,
        'hidden_at': _potential_datetime_to_json(comment.hidden_at),
        'hidden_by_id': _potential_user_to_json(moderator),
    }


def _potential_datetime_to_json(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if (dt is not None) else None


def _potential_user_to_json(user: Optional[User]) -> Optional[dict[str, Any]]:
    return _user_to_json(user) if (user is not None) else None


def _user_to_json(user: User) -> dict[str, Any]:
    return {
        'user_id': str(user.id),
        'screen_name': user.screen_name,
        'suspended': user.suspended,
        'deleted': user.deleted,
        'avatar_url': user.avatar_url,
        'is_orga': user.is_orga,
    }


blueprint.add_url_rule(
    '/match_comments/<uuid:comment_id>',
    endpoint='view',
    build_only=True,
)


@blueprint.post('/match_comments')
@api_token_required
@respond_created
def create():
    """Create a comment on a match."""
    req = _parse_request(CreateMatchCommentRequest)

    match = match_service.find_match(req['match_id'])
    if not match:
        abort(400, 'Unknown match ID')

    creator = user_service.find_active_user(req['creator_id'])
    if not creator:
        abort(400, 'Creator ID does not reference an active user.')

    body = req['body'].strip()

    comment = comment_service.create_comment(match.id, creator.id, body)

    tourney_signals.match_comment_created.send(None, comment_id=comment.id)

    return url_for('.view', comment_id=comment.id)


@blueprint.patch('/match_comments/<uuid:comment_id>')
@api_token_required
@respond_no_content
def update(comment_id):
    """Update a comment on a match."""
    comment = _get_comment_or_404(comment_id)

    req = _parse_request(UpdateMatchCommentRequest)

    editor = user_service.find_active_user(req['editor_id'])
    if not editor:
        abort(400, 'Editor ID does not reference an active user.')

    body = req['body'].strip()

    comment_service.update_comment(comment.id, editor.id, body)


@blueprint.post('/match_comments/<uuid:comment_id>/flags/hidden')
@api_token_required
@respond_no_content
def hide(comment_id):
    """Hide the match comment."""
    comment = _get_comment_or_404(comment_id)

    req = _parse_request(ModerateMatchCommentRequest)

    initiator = user_service.find_active_user(req['initiator_id'])
    if not initiator:
        abort(400, 'Initiator ID does not reference an active user.')

    comment_service.hide_comment(comment.id, initiator.id)


@blueprint.delete('/match_comments/<uuid:comment_id>/flags/hidden')
@api_token_required
@respond_no_content
def unhide(comment_id):
    """Un-hide the match comment."""
    comment = _get_comment_or_404(comment_id)

    req = _parse_request(ModerateMatchCommentRequest)

    initiator = user_service.find_active_user(req['initiator_id'])
    if not initiator:
        abort(400, 'Initiator ID does not reference an active user.')

    comment_service.unhide_comment(comment.id, initiator.id)


def _get_match_or_404(match_id: MatchID) -> Match:
    match = match_service.find_match(match_id)

    if match is None:
        abort(404)

    return match


def _get_comment_or_404(comment_id: MatchCommentID) -> MatchComment:
    comment = comment_service.find_comment(comment_id)

    if comment is None:
        abort(404)

    return comment


def _parse_request(schema_class: SchemaMeta) -> dict[str, Any]:
    schema = schema_class()
    request_data = request.get_json()

    try:
        req = schema.load(request_data)
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    return req
