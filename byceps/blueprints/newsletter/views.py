"""
byceps.blueprints.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import abort, g

from ...services.newsletter import command_service, service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.views import respond_no_content


blueprint = create_blueprint('newsletter', __name__)


@blueprint.route('/lists/<list_id>/subscription', methods=['POST'])
@respond_no_content
def subscribe(list_id):
    list_ = _get_list_or_404(list_id)
    user = _get_current_user_or_404()
    expressed_at = datetime.utcnow()

    command_service.subscribe(user.id, list_.id, expressed_at)

    flash_success(f'Du hast dich zum Newsletter "{list_.title}" angemeldet.')


@blueprint.route('/lists/<list_id>/subscription', methods=['DELETE'])
@respond_no_content
def unsubscribe(list_id):
    list_ = _get_list_or_404(list_id)
    user = _get_current_user_or_404()
    expressed_at = datetime.utcnow()

    command_service.unsubscribe(user.id, list_.id, expressed_at)

    flash_success(f'Du hast dich vom Newsletter "{list_.title}" abgemeldet.')


def _get_current_user_or_404():
    user = g.current_user

    if not user.is_active:
        abort(404)

    return user


def _get_list_or_404(list_id):
    list_ = service.find_list(list_id)

    if list_ is None:
        abort(404)

    return list_
