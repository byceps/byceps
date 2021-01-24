"""
byceps.blueprints.site.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import abort, g

from ....services.newsletter import command_service, service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.views import login_required, respond_no_content


blueprint = create_blueprint('newsletter', __name__)


@blueprint.route('/lists/<list_id>/subscription', methods=['POST'])
@login_required
@respond_no_content
def subscribe(list_id):
    list_ = _get_list_or_404(list_id)
    expressed_at = datetime.utcnow()

    command_service.subscribe(g.user.id, list_.id, expressed_at)

    flash_success(f'Du hast dich zum Newsletter "{list_.title}" angemeldet.')


@blueprint.route('/lists/<list_id>/subscription', methods=['DELETE'])
@login_required
@respond_no_content
def unsubscribe(list_id):
    list_ = _get_list_or_404(list_id)
    expressed_at = datetime.utcnow()

    command_service.unsubscribe(g.user.id, list_.id, expressed_at)

    flash_success(f'Du hast dich vom Newsletter "{list_.title}" abgemeldet.')


def _get_list_or_404(list_id):
    list_ = service.find_list(list_id)

    if list_ is None:
        abort(404)

    return list_
