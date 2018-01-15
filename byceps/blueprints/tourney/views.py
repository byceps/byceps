"""
byceps.blueprints.tourney.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request, url_for

from ...services.tourney import service as tourney_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated
from ...util.views import respond_created

from . import signals


blueprint = create_blueprint('tourney', __name__)


# -------------------------------------------------------------------- #
# match comments


@blueprint.route('/matches/<uuid:match_id>/comments')
@templated
def match_comments_view(match_id):
    """Render the comments on a match."""
    match = _get_match_or_404(match_id)

    comments = tourney_service.get_match_comments(match.id)

    return {
        'comments': comments,
    }


blueprint.add_url_rule(
    '/matches/<uuid:match_id>/comments/<uuid:comment_id>',
    endpoint='match_comment_view',
    build_only=True)


@blueprint.route('/matches/<uuid:match_id>/comments', methods=['POST'])
@respond_created
def match_comment_create(match_id):
    """Create a comment on a match."""
    if not g.current_user.is_active:
        abort(403)

    match = _get_match_or_404(match_id)

    body = request.form['body'].strip()

    comment = tourney_service.create_match_comment(match_id, g.current_user.id,
                                                   body)

    signals.match_comment_created.send(None, comment_id=comment.id)

    return url_for('.match_comment_view',
                   match_id=match.id,
                   comment_id=comment.id)


def _get_match_or_404(match_id):
    match = tourney_service.find_match(match_id)

    if match is None:
        abort(404)

    return match
