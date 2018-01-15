"""
byceps.blueprints.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.newsletter import service as newsletter_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.views import respond_no_content


blueprint = create_blueprint('newsletter', __name__)


@blueprint.route('/subscription', methods=['POST'])
@respond_no_content
def subscribe():
    user = _get_current_user_or_404()

    newsletter_service.subscribe(user.id, g.brand_id)

    flash_success('Du hast dich zum Newsletter angemeldet.')


@blueprint.route('/subscription', methods=['DELETE'])
@respond_no_content
def unsubscribe():
    user = _get_current_user_or_404()

    newsletter_service.unsubscribe(user.id, g.brand_id)

    flash_success('Du hast dich vom Newsletter abgemeldet.')


def _get_current_user_or_404():
    user = g.current_user

    if not user.is_active:
        abort(404)

    return user
