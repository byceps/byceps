# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import request, url_for

from ...util.framework import create_blueprint
from ...util.views import respond_created

from .models import Match, MatchComment


blueprint = create_blueprint('tourney', __name__)


# -------------------------------------------------------------------- #
# match comments


blueprint.add_url_rule(
    '/matches/<match_id>/comments/<comment_id>',
    endpoint='match_comment_view',
    build_only=True)


@blueprint.route('/matches/<match_id>/comments', methods=['POST'])
@respond_created
def match_comment_create(match_id):
    """Create a comment on a match."""
    match = Match.query.get_or_404(match_id)

    #body = request.form['body'].strip()
    body = 'enis'

    comment = MatchComment.create(match, body)

    return url_for('.match_comment_view',
                   match_id=match.id,
                   comment_id=comment.id)
