# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from ...util.framework import create_blueprint
from ...util.templating import templated
from ...util.views import jsonified, textified

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..newsletter.models import SubscriptionState

from .authorization import NewsletterPermission
from .service import count_subscriptions_by_state, get_subscribers, \
    get_user_subscription_states_for_brand


blueprint = create_blueprint('newsletter_admin', __name__)


permission_registry.register_enum(NewsletterPermission)


@blueprint.route('/')
@permission_required(NewsletterPermission.view_subscriptions)
@templated
def index():
    """List brands to choose from."""
    brands = Brand.query.all()
    return {'brands': brands}


@blueprint.route('/subscriptions/<brand_id>')
@permission_required(NewsletterPermission.view_subscriptions)
@templated
def view_subscriptions(brand_id):
    """Show user subscription states for that brand."""
    brand = Brand.query.get_or_404(brand_id)

    subscription_states = list(get_user_subscription_states_for_brand(brand))
    subscription_states.sort(
        key=lambda user_and_state: user_and_state[0].screen_name.lower())

    totals = count_subscriptions_by_state(subscription_states)

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
    brand = Brand.query.get_or_404(brand_id)

    subscribers = get_subscribers(brand)

    exports = list(map(assemble_subscriber_export, subscribers))

    return {'subscribers': exports}


def assemble_subscriber_export(user):
    return {
        'screen_name': user.screen_name,
        'email_address': user.email_address,
    }


@blueprint.route('/subscriptions/<brand_id>/export_email_addresses')
@permission_required(NewsletterPermission.export_subscribers)
@textified
def export_subscriber_email_addresses(brand_id):
    """Export the email addresses of enabled users which are currently
    subscribed to the newsletter for this brand as plaintext, with one
    address per row.
    """
    brand = Brand.query.get_or_404(brand_id)

    subscribers = get_subscribers(brand)
    email_addresses = map(attrgetter('email_address'), subscribers)
    return '\n'.join(email_addresses)
