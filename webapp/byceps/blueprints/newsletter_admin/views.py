# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..brand.models import Brand
from ..newsletter.models import NewsletterSubscriptionState

from .authorization import NewsletterPermission
from .models import count_subscriptions_by_state, get_subscriptions_for_brand


blueprint = create_blueprint('newsletter_admin', __name__)


permission_registry.register_enum(NewsletterPermission)


@blueprint.route('/')
@permission_required(NewsletterPermission.view_stats)
@templated
def index():
    """List brands to choose from."""
    brands = Brand.query.all()
    return {'brands': brands}


@blueprint.route('/subscriptions/<brand_id>')
@permission_required(NewsletterPermission.view_stats)
@templated
def view_subscriptions_for_brand(brand_id):
    """Show user subscriptions for that brand."""
    brand = Brand.query.get_or_404(brand_id)

    subscriptions = list(get_subscriptions_for_brand(brand))

    totals = count_subscriptions_by_state(subscriptions)

    return {
        'brand': brand,
        'subscriptions': subscriptions,
        'totals': totals,
        'State': NewsletterSubscriptionState,
    }
