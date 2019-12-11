"""
byceps.blueprints.api.tourney.match.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, jsonify, request, url_for
from marshmallow import ValidationError

from .....services.tourney import match_comment_service, match_service
from .....services.user import service as user_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import respond_created, respond_no_content

from ...decorators import api_token_required

from .. import signals

from .schemas import CreateMatchCommentRequest, ModerateMatchCommentRequest


blueprint = create_blueprint('api_tourney_match', __name__)


# -------------------------------------------------------------------- #
# match comments


@blueprint.route('/<uuid:match_id>/comments')
@api_token_required
@templated
def comments_view(match_id):
    """Render the comments on a match."""
    match = _get_match_or_404(match_id)

    party_id = request.args.get('party_id')

    comments = match_comment_service.get_comments(
        match.id, party_id=party_id, include_hidden=False
    )

    return {
        'comments': comments,
    }


@blueprint.route('/<uuid:match_id>/comments.json')
@api_token_required
def comments_view_as_json(match_id):
    """Render the comments on a match as JSON."""
    match = _get_match_or_404(match_id)

    party_id = request.args.get('party_id')

    comments = match_comment_service.get_comments(
        match.id, party_id=party_id, include_hidden=True
    )

    comment_dtos = list(map(_comment_to_json, comments))

    return jsonify({
        'comments': comment_dtos,
    })


def _comment_to_json(comment):
    creator = comment.creator

    return {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': {
            'user_id': creator.id,
            'screen_name': creator.screen_name,
            'suspended': creator.suspended,
            'deleted': creator.deleted,
            'avatar_url': creator.avatar_url,
            'is_orga': creator.is_orga,
        },
        'body': comment.body_rendered,
        'hidden': comment.hidden,
        'hidden_at': comment.hidden_at.isoformat() \
                     if (comment.hidden_at is not None) else None,
        'hidden_by_id': comment.hidden_by_id,
    }


blueprint.add_url_rule(
    '/<uuid:match_id>/comments/<uuid:comment_id>',
    endpoint='comment_view',
    build_only=True,
)


@blueprint.route('/<uuid:match_id>/comments', methods=['POST'])
@api_token_required
@respond_created
def comment_create(match_id):
    """Create a comment on a match."""
    match = _get_match_or_404(match_id)

    schema = CreateMatchCommentRequest()
    try:
        req = schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    creator = user_service.find_active_user(req['creator_id'])
    if not creator:
        abort(400, 'Creator ID does not reference an active user.')

    body = req['body'].strip()

    comment = match_comment_service.create_comment(match.id, creator.id, body)

    signals.match_comment_created.send(None, comment_id=comment.id)

    return url_for('.comment_view', match_id=match.id, comment_id=comment.id)


@blueprint.route(
    '/<uuid:match_id>/comments/<uuid:comment_id>/flags/hidden', methods=['POST']
)
@api_token_required
@respond_no_content
def comment_hide(match_id, comment_id):
    """Hide the match comment."""
    schema = ModerateMatchCommentRequest()
    try:
        req = schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    initiator = user_service.find_active_user(req['initiator_id'])
    if not initiator:
        abort(400, 'Initiator ID does not reference an active user.')

    match_comment_service.hide_comment(comment_id, initiator.id)


@blueprint.route(
    '/<uuid:match_id>/comments/<uuid:comment_id>/flags/hidden',
    methods=['DELETE'],
)
@api_token_required
@respond_no_content
def comment_unhide(match_id, comment_id):
    """Un-hide the match comment."""
    schema = ModerateMatchCommentRequest()
    try:
        req = schema.load(request.get_json())
    except ValidationError as e:
        abort(400, str(e.normalized_messages()))

    initiator = user_service.find_active_user(req['initiator_id'])
    if not initiator:
        abort(400, 'Initiator ID does not reference an active user.')

    match_comment_service.unhide_comment(comment_id, initiator.id)


def _get_match_or_404(match_id):
    match = match_service.find_match(match_id)

    if match is None:
        abort(404)

    return match
