"""
byceps.blueprints.site.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import abort, g
from flask_babel import gettext

from ....services.newsletter import command_service, service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.views import login_required, respond_no_content


blueprint = create_blueprint('newsletter', __name__)


@blueprint.post('/lists/<list_id>/subscription')
@login_required
@respond_no_content
def subscribe(list_id):
    list_ = _get_list_or_404(list_id)
    expressed_at = datetime.utcnow()

    command_service.subscribe(g.user.id, list_.id, expressed_at)

    flash_success(
        gettext(
            'You have subscribed to newsletter "%(title)s".',
            title=list_.title,
        )
    )


@blueprint.delete('/lists/<list_id>/subscription')
@login_required
@respond_no_content
def unsubscribe(list_id):
    list_ = _get_list_or_404(list_id)
    expressed_at = datetime.utcnow()

    command_service.unsubscribe(g.user.id, list_.id, expressed_at)

    flash_success(
        gettext(
            'You have unsubscribed from newsletter "%(title)s".',
            title=list_.title,
        )
    )


def _get_list_or_404(list_id):
    list_ = service.find_list(list_id)

    if list_ is None:
        abort(404)

    return list_
