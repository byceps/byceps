"""
byceps.services.tourney.match_comment.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import datetime
from itertools import chain
from typing import Any

from flask import abort, jsonify, request, url_for
from pydantic import BaseModel, ValidationError

from byceps.blueprints.api.decorators import api_token_required
from byceps.services.orga_team import orga_team_service
from byceps.services.tourney import (
    signals as tourney_signals,
    tourney_match_comment_service,
    tourney_match_service,
)
from byceps.services.tourney.models import (
    Match,
    MatchComment,
    MatchCommentID,
    MatchID,
)
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import respond_created, respond_no_content

from .models import (
    CreateMatchCommentRequest,
    ModerateMatchCommentRequest,
    UpdateMatchCommentRequest,
)


blueprint = create_blueprint('tourney_match_comment_api', __name__)


@blueprint.get('/match_comments/<uuid:comment_id>')
@api_token_required
def get_comment(comment_id):
    """Return the comment."""
    comment = _get_comment_or_404(comment_id)

    party_id = request.args.get('party_id')
    if party_id:
        user_ids = set(_get_user_ids_for_comment(comment))
        orga_ids = orga_team_service.select_orgas_for_party(user_ids, party_id)
    else:
        orga_ids = set()

    comment_dict = _comment_to_json(comment, orga_ids)

    return jsonify(comment_dict)


@blueprint.get('/matches/<uuid:match_id>/comments')
@api_token_required
def get_comments_for_match(match_id):
    """Return the comments on the match."""
    match = _get_match_or_404(match_id)

    comments = tourney_match_comment_service.get_comments(
        match.id, include_hidden=True
    )

    party_id = request.args.get('party_id')
    if party_id:
        user_ids = set(
            chain.from_iterable(map(_get_user_ids_for_comment, comments))
        )
        orga_ids = orga_team_service.select_orgas_for_party(user_ids, party_id)
    else:
        orga_ids = set()

    comment_dicts = [
        _comment_to_json(comment, orga_ids) for comment in comments
    ]

    return jsonify(
        {
            'comments': comment_dicts,
        }
    )


def _get_user_ids_for_comment(comment: MatchComment) -> Iterator[UserID]:
    yield comment.created_by.id

    last_editor = comment.last_edited_by
    if last_editor:
        yield last_editor.id

    moderator = comment.hidden_by
    if moderator:
        yield moderator.id


def _comment_to_json(
    comment: MatchComment, orga_ids: set[UserID]
) -> dict[str, Any]:
    creator = comment.created_by
    last_editor = comment.last_edited_by
    moderator = comment.hidden_by

    return {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': _user_to_json(creator, orga_ids),
        'body_text': comment.body_text,
        'body_html': comment.body_html,
        'last_edited_at': _potential_datetime_to_json(comment.last_edited_at),
        'last_editor': _potential_user_to_json(last_editor, orga_ids),
        'hidden': comment.hidden,
        'hidden_at': _potential_datetime_to_json(comment.hidden_at),
        'hidden_by': _potential_user_to_json(moderator, orga_ids),
    }


def _potential_datetime_to_json(dt: datetime | None) -> str | None:
    return dt.isoformat() if (dt is not None) else None


def _potential_user_to_json(
    user: User | None, orga_ids: set[UserID]
) -> dict[str, Any] | None:
    return _user_to_json(user, orga_ids) if (user is not None) else None


def _user_to_json(user: User, orga_ids: set[UserID]) -> dict[str, Any]:
    return {
        'user_id': str(user.id),
        'screen_name': user.screen_name,
        'suspended': user.suspended,
        'deleted': user.deleted,
        'avatar_url': user.avatar_url,
        'is_orga': user.id in orga_ids,
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

    match = tourney_match_service.find_match(req.match_id)
    if not match:
        abort(400, 'Unknown match ID')

    creator = user_service.find_active_user(req.creator_id)
    if not creator:
        abort(400, 'Creator ID does not reference an active user.')

    body = req.body.strip()

    comment = tourney_match_comment_service.create_comment(
        match.id, creator, body
    )

    tourney_signals.match_comment_created.send(
        None, comment_id=comment.id, creator_id=creator.id, match_id=match.id
    )

    return url_for('.view', comment_id=comment.id)


@blueprint.patch('/match_comments/<uuid:comment_id>')
@api_token_required
@respond_no_content
def update(comment_id):
    """Update a comment on a match."""
    comment = _get_comment_or_404(comment_id)

    req = _parse_request(UpdateMatchCommentRequest)

    editor = user_service.find_active_user(req.editor_id)
    if not editor:
        abort(400, 'Editor ID does not reference an active user.')

    body = req.body.strip()

    tourney_match_comment_service.update_comment(comment.id, editor, body)


@blueprint.post('/match_comments/<uuid:comment_id>/flags/hidden')
@api_token_required
@respond_no_content
def hide(comment_id):
    """Hide the match comment."""
    comment = _get_comment_or_404(comment_id)

    req = _parse_request(ModerateMatchCommentRequest)

    initiator = user_service.find_active_user(req.initiator_id)
    if not initiator:
        abort(400, 'Initiator ID does not reference an active user.')

    tourney_match_comment_service.hide_comment(comment.id, initiator)


@blueprint.delete('/match_comments/<uuid:comment_id>/flags/hidden')
@api_token_required
@respond_no_content
def unhide(comment_id):
    """Un-hide the match comment."""
    comment = _get_comment_or_404(comment_id)

    req = _parse_request(ModerateMatchCommentRequest)

    initiator = user_service.find_active_user(req.initiator_id)
    if not initiator:
        abort(400, 'Initiator ID does not reference an active user.')

    tourney_match_comment_service.unhide_comment(comment.id, initiator)


def _get_match_or_404(match_id: MatchID) -> Match:
    match = tourney_match_service.find_match(match_id)

    if match is None:
        abort(404)

    return match


def _get_comment_or_404(comment_id: MatchCommentID) -> MatchComment:
    comment = tourney_match_comment_service.find_comment(comment_id)

    if comment is None:
        abort(404)

    return comment


def _parse_request(model_class: type[BaseModel]) -> BaseModel:
    try:
        return model_class.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())
