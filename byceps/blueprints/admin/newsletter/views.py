"""
byceps.blueprints.admin.newsletter.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from operator import attrgetter

from flask import abort
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand, BrandID
from byceps.services.newsletter import (
    newsletter_command_service,
    newsletter_service,
)
from byceps.services.newsletter.models import List, ListID
from byceps.services.user import user_stats_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    jsonified,
    permission_required,
    redirect_to,
    textified,
)


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


def _add_subscriber_count(list_: List) -> ListWithStats:
    subscriber_count = newsletter_service.count_subscribers(list_.id)

    return ListWithStats(list_.id, list_.title, subscriber_count)


@blueprint.get('/for_brand/<brand_id>/create')
@permission_required('newsletter.administrate')
@templated
def create_brand_list_form(brand_id):
    """Show form to create a list for that brand."""
    brand = _get_brand_or_404(brand_id)

    return {
        'brand': brand,
    }


@blueprint.post('/for_brand/<brand_id>')
@permission_required('newsletter.administrate')
def create_brand_list(brand_id):
    """Create a list for that brand."""
    brand = _get_brand_or_404(brand_id)

    list_ = newsletter_command_service.create_list(brand.id, brand.title)

    flash_success(gettext('Subscription list has been created.'))

    return redirect_to('.view_subscriptions', list_id=list_.id)


@blueprint.get('/lists/<list_id>/subscriptions')
@permission_required('newsletter.view_subscriptions')
@templated
def view_subscriptions(list_id):
    """Show user subscription states for that list."""
    list_ = _find_list(list_id)
    if list_ is None:
        brand = _find_brand(list_id)
        if brand is not None:
            return redirect_to('.create_brand_list_form', brand_id=brand.id)
        else:
            abort(404)

    subscription_count = newsletter_service.count_subscribers(list_.id)
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


def _get_brand_or_404(brand_id: BrandID) -> Brand:
    brand = _find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _find_brand(brand_id: BrandID) -> Brand | None:
    return brand_service.find_brand(brand_id)


def _get_list_or_404(list_id: ListID) -> List:
    list_ = _find_list(list_id)

    if list_ is None:
        abort(404)

    return list_


def _find_list(list_id: ListID) -> List | None:
    return newsletter_service.find_list(list_id)
