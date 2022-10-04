"""
byceps.blueprints.admin.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from operator import attrgetter

from flask import abort

from ....services.newsletter import service as newsletter_service
from ....services.newsletter.transfer.models import List
from ....services.user import user_stats_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import jsonified, permission_required, textified


blueprint = create_blueprint('newsletter_admin', __name__)


@dataclass(frozen=True)
class ListWithStats(List):
    subscriber_count: int


@blueprint.get('/lists')
@permission_required('newsletter.view_subscriptions')
@templated
def index():
    """List all lists."""
    lists = newsletter_service.get_all_lists()

    lists_with_stats = list(map(_add_subscriber_count, lists))

    return {
        'lists': lists_with_stats,
    }


def _add_subscriber_count(list_):
    subscriber_count = newsletter_service.count_subscribers_for_list(list_.id)

    return ListWithStats(list_.id, list_.title, subscriber_count)


@blueprint.get('/lists/<list_id>/subscriptions')
@permission_required('newsletter.view_subscriptions')
@templated
def view_subscriptions(list_id):
    """Show user subscription states for that list."""
    list_ = _get_list_or_404(list_id)

    subscription_count = newsletter_service.count_subscribers_for_list(list_.id)
    user_count = user_stats_service.count_users()

    return {
        'list_': list_,
        'subscription_count': subscription_count,
        'user_count': user_count,
    }


@blueprint.get('/lists/<list_id>/subscriptions/export')
@permission_required('newsletter.export_subscribers')
@jsonified
def export_subscribers(list_id):
    """Export the screen names and email addresses of enabled users
    which are currently subscribed to that list as JSON.
    """
    list_ = _get_list_or_404(list_id)

    subscribers = newsletter_service.get_subscribers(list_.id)

    exports = list(map(assemble_subscriber_export, subscribers))

    return {'subscribers': exports}


def assemble_subscriber_export(subscriber):
    return {
        'screen_name': subscriber.screen_name,
        'email_address': subscriber.email_address,
    }


@blueprint.get('/lists/<list_id>/subscriptions/email_addresses/export')
@permission_required('newsletter.export_subscribers')
@textified
def export_subscriber_email_addresses(list_id):
    """Export the email addresses of enabled users which are currently
    subscribed to that list as plaintext, with one address per row.
    """
    list_ = _get_list_or_404(list_id)

    subscribers = newsletter_service.get_subscribers(list_.id)
    email_addresses = map(attrgetter('email_address'), subscribers)
    return '\n'.join(email_addresses)


def _get_list_or_404(list_id):
    list_ = newsletter_service.find_list(list_id)

    if list_ is None:
        abort(404)

    return list_
