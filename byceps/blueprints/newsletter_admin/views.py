"""
byceps.blueprints.newsletter_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import abort

from ...services.brand import service as brand_service
from ...services.newsletter import service as newsletter_service
from ...services.newsletter.types import SubscriptionState
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated
from ...util.views import jsonified, textified

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import NewsletterPermission


blueprint = create_blueprint('newsletter_admin', __name__)


permission_registry.register_enum(NewsletterPermission)


@blueprint.route('/subscriptions/<brand_id>')
@permission_required(NewsletterPermission.view_subscriptions)
@templated
def view_subscriptions(brand_id):
    """Show user subscription states for that brand."""
    brand = _get_brand_or_404(brand_id)

    subscription_states = list(newsletter_service
        .get_user_subscription_states_for_brand(brand.id))
    subscription_states.sort(
        key=lambda user_and_state: user_and_state[0].screen_name.lower())

    totals = newsletter_service.count_subscriptions_by_state(subscription_states)

    return {
        'brand': brand,
        'subscription_states': subscription_states,
        'totals': totals,
        'State': SubscriptionState,
    }


@blueprint.route('/subscriptions/<brand_id>/export')
@permission_required(NewsletterPermission.export_subscribers)
@jsonified
def export_subscribers(brand_id):
    """Export the screen names and email addresses of enabled users
    which are currently subscribed to the newsletter for this brand
    as JSON.
    """
    brand = _get_brand_or_404(brand_id)

    subscribers = newsletter_service.get_subscribers(brand.id)

    exports = list(map(assemble_subscriber_export, subscribers))

    return {'subscribers': exports}


def assemble_subscriber_export(subscriber):
    return {
        'screen_name': subscriber.screen_name,
        'email_address': subscriber.email_address,
    }


@blueprint.route('/subscriptions/<brand_id>/export_email_addresses')
@permission_required(NewsletterPermission.export_subscribers)
@textified
def export_subscriber_email_addresses(brand_id):
    """Export the email addresses of enabled users which are currently
    subscribed to the newsletter for this brand as plaintext, with one
    address per row.
    """
    brand = _get_brand_or_404(brand_id)

    subscribers = newsletter_service.get_subscribers(brand.id)
    email_addresses = map(attrgetter('email_address'), subscribers)
    return '\n'.join(email_addresses)


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand
