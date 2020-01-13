"""
byceps.blueprints.api.tourney.match.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict

from flask import abort, jsonify, request, url_for
from marshmallow import ValidationError
from marshmallow.schema import SchemaMeta

from ......services.tourney import (
    match_comment_service as comment_service,
    match_service,
)
from ......services.user import service as user_service
from ......util.framework.blueprint import create_blueprint
from ......util.views import respond_created, respond_no_content

from ....decorators import api_token_required

from ... import signals

from .schemas import (
    CreateMatchCommentRequest,
    ModerateMatchCommentRequest,
    UpdateMatchCommentRequest,
)


blueprint = create_blueprint('api_tourney_match_comments', __name__)


@blueprint.route('/matches/<uuid:match_id>/comments')
@api_token_required
def view_for_match(match_id):
    """Render the comments on a match as JSON."""
    match = _get_match_or_404(match_id)

    party_id = request.args.get('party_id')

    comments = comment_service.get_comments(
        match.id, party_id=party_id, include_hidden=True
    )

    comment_dtos = list(map(_comment_to_json, comments))

    return jsonify({
        'comments': comment_dtos,
    })


def _comment_to_json(comment):
    creator = comment.creator
    last_editor = comment.last_edited_by

    return {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': _user_to_json(creator),
        'body': comment.body_rendered,
        'last_edited_at': comment.last_edited_at.isoformat()
            if comment.last_edited_at is not None
            else None,
        'last_editor': _user_to_json(last_editor)
            if last_editor is not None
            else None,
        'hidden': comment.hidden,
        'hidden_at': comment.hidden_at.isoformat()
            if comment.hidden_at is not None
            else None,
        'hidden_by_id': comment.hidden_by_id,
    }


def _user_to_json(user):
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


@blueprint.route('/match_comments', methods=['POST'])
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

    signals.match_comment_created.send(None, comment_id=comment.id)

    return url_for('.view', comment_id=comment.id)


@blueprint.route('/match_comments/<uuid:comment_id>', methods=['PATCH'])
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


@blueprint.route(
    '/match_comments/<uuid:comment_id>/flags/hidden', methods=['POST']
)
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


@blueprint.route(
    '/match_comments/<uuid:comment_id>/flags/hidden',
    methods=['DELETE'],
)
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


def _get_match_or_404(match_id):
    match = match_service.find_match(match_id)

    if match is None:
        abort(404)

    return match


def _get_comment_or_404(comment_id):
    comment = comment_service.find_comment(comment_id)

    if comment is None:
        abort(404)

    return comment


def _parse_request(schema_class: SchemaMeta) -> Dict[str, Any]:
    schema = schema_class()
    request_data = request.get_json()

    try:
        req = schema.load(request_data)
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    return req
