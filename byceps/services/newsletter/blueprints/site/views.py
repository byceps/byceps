"""
byceps.services.newsletter.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import abort, g
from flask_babel import gettext

from byceps.services.newsletter import (
    newsletter_command_service,
    newsletter_service,
    signals as newsletter_signals,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.result import Err, Ok
from byceps.util.views import login_required, respond_no_content


blueprint = create_blueprint('newsletter', __name__)


@blueprint.post('/lists/<list_id>/subscription')
@login_required
@respond_no_content
def subscribe(list_id):
    list_ = _get_list_or_404(list_id)
    user = g.user.as_user()
    expressed_at = datetime.utcnow()
    initiator = user

    match newsletter_command_service.subscribe_user_to_list(
        user, list_, expressed_at, initiator
    ):
        case Ok((_, event)):
            flash_success(
                gettext(
                    'You have subscribed to newsletter "%(title)s".',
                    title=list_.title,
                )
            )

            newsletter_signals.newsletter_subscribed.send(None, event=event)
        case Err(e):
            flash_error(e)


@blueprint.delete('/lists/<list_id>/subscription')
@login_required
@respond_no_content
def unsubscribe(list_id):
    list_ = _get_list_or_404(list_id)
    user = g.user.as_user()
    expressed_at = datetime.utcnow()
    initiator = user

    match newsletter_command_service.unsubscribe_user_from_list(
        user, list_, expressed_at, initiator
    ):
        case Ok((_, event)):
            flash_success(
                gettext(
                    'You have unsubscribed from newsletter "%(title)s".',
                    title=list_.title,
                )
            )

            newsletter_signals.newsletter_unsubscribed.send(None, event=event)
        case Err(e):
            flash_error(e)


def _get_list_or_404(list_id):
    list_ = newsletter_service.find_list(list_id)

    if list_ is None:
        abort(404)

    return list_
