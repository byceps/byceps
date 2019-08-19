"""
byceps.blueprints.admin.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from attr import attrs
from flask import abort

from ....services.newsletter import service as newsletter_service
from ....services.newsletter.transfer.models import List
from ....services.newsletter.types import SubscriptionState
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import jsonified, textified

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import NewsletterPermission


blueprint = create_blueprint('newsletter_admin', __name__)


permission_registry.register_enum(NewsletterPermission)


@attrs(auto_attribs=True, frozen=True, slots=True)
class ListWithStats(List):
    subscriber_count: int


@blueprint.route('/lists')
@permission_required(NewsletterPermission.view_subscriptions)
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


@blueprint.route('/lists/<list_id>/subscriptions')
@permission_required(NewsletterPermission.view_subscriptions)
@templated
def view_subscriptions(list_id):
    """Show user subscription states for that list."""
    list_ = _get_list_or_404(list_id)

    totals = newsletter_service.count_subscriptions_by_state(list_.id)

    return {
        'list_': list_,
        'totals': totals,
        'State': SubscriptionState,
    }


@blueprint.route('/lists/<list_id>/subscriptions/export')
@permission_required(NewsletterPermission.export_subscribers)
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


@blueprint.route('/lists/<list_id>/subscriptions/email_addresses/export')
@permission_required(NewsletterPermission.export_subscribers)
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
