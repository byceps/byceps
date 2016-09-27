# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_badge.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ...services.user_badge import service as badge_service
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..user import service as user_service


blueprint = create_blueprint('user_badge', __name__)


@blueprint.route('/')
@templated
def index():
    """List all badges."""
    badges = badge_service.get_all_badges()

    return {
        'badges': badges,
    }


@blueprint.route('/<uuid:badge_id>')
@templated
def view(badge_id):
    """Show information about a badge."""
    badge = badge_service.find_badge(badge_id)

    if badge is None:
        abort(404)

    awardings = badge_service.get_awardings_of_badge(badge.id)
    recipient_ids = [awarding.user_id for awarding in awardings]
    recipients = user_service.get_users_with_avatars(recipient_ids)

    return {
        'badge': badge,
        'recipients': recipients,
    }
