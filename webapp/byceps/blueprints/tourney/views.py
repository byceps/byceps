# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g, request, url_for

from ...util.framework import create_blueprint
from ...util.templating import templated
from ...util.views import respond_created

from .models.match import Match
from . import service
from . import signals


blueprint = create_blueprint('tourney', __name__)


# -------------------------------------------------------------------- #
# match comments


@blueprint.route('/matches/<uuid:match_id>/comments')
@templated
def match_comments_view(match_id):
    """Render the comments on a match."""
    match = Match.query.get_or_404(match_id)

    comments = service.get_match_comments(match)

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
    match = Match.query.get_or_404(match_id)

    body = request.form['body'].strip()

    comment = service.create_match_comment(match, g.current_user, body)

    signals.match_comment_create.send(None, comment=comment)

    return url_for('.match_comment_view',
                   match_id=match.id,
                   comment_id=comment.id)
