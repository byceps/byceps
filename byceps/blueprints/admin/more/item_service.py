"""
byceps.blueprints.admin.more.item_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from flask import url_for
from flask_babel import gettext

from byceps.services.brand.models import Brand
from byceps.services.party.models import Party
from byceps.services.site.models import Site


@dataclass(frozen=True)
class MoreItem:
    label: str
    icon: str
    url: str
    required_permission: str
    precondition: bool = True


def get_global_items() -> list[MoreItem]:
    return [
        MoreItem(
            label=gettext('Permissions'),
            icon='permission',
            url=url_for('authz_admin.role_index'),
            required_permission='role.view',
        ),
        MoreItem(
            label=gettext('Languages'),
            icon='language',
            url=url_for('language_admin.index'),
            required_permission='admin.maintain',
        ),
        MoreItem(
            label=gettext('Global Snippets'),
            icon='snippet',
            url=url_for(
                'snippet_admin.index_for_scope',
                scope_type='global',
                scope_name='global',
            ),
            required_permission='snippet.view',
        ),
        MoreItem(
            label=gettext('Consents'),
            icon='consent',
            url=url_for('consent_admin.subject_index'),
            required_permission='consent.administrate',
        ),
        MoreItem(
            label=gettext('Newsletters'),
            icon='email',
            url=url_for('newsletter_admin.index'),
            required_permission='newsletter.view_subscriptions',
        ),
        MoreItem(
            label=gettext('User Badges'),
            icon='badge',
            url=url_for('user_badge_admin.index'),
            required_permission='user_badge.view',
        ),
        MoreItem(
            label=gettext('Identity Tags'),
            icon='identity-tag',
            url=url_for('authn_identity_tag_admin.index'),
            required_permission='authn_identity_tag.view',
        ),
        MoreItem(
            label=gettext('Payment gateways'),
            icon='payment',
            url=url_for('shop_payment_admin.index'),
            required_permission='shop.view',
        ),
        MoreItem(
            label=gettext('API'),
            icon='api',
            url=url_for('api_admin.index'),
            required_permission='api.administrate',
        ),
        MoreItem(
            label=gettext('Webhooks'),
            icon='webhook',
            url=url_for('webhook_admin.index'),
            required_permission='webhook.view',
        ),
        MoreItem(
            label=gettext('Maintenance'),
            icon='administrate',
            url=url_for('maintenance_admin.index'),
            required_permission='admin.maintain',
        ),
    ]


def get_brand_items(brand: Brand) -> list[MoreItem]:
    return [
        MoreItem(
            label=gettext('Newsletter Subscriptions'),
            icon='email',
            url=url_for(
                'newsletter_admin.view_subscriptions', list_id=brand.id
            ),
            required_permission='newsletter.view_subscriptions',
        ),
        MoreItem(
            label=gettext('Discussion Boards'),
            icon='board',
            url=url_for('board_admin.board_index_for_brand', brand_id=brand.id),
            required_permission='board_category.view',
        ),
        MoreItem(
            label=gettext('Galleries'),
            icon='gallery',
            url=url_for(
                'gallery_admin.gallery_index_for_brand', brand_id=brand.id
            ),
            required_permission='gallery.administrate',
        ),
        MoreItem(
            label=gettext('Most Frequent Attendees'),
            icon='users',
            url=url_for('attendance_admin.view_for_brand', brand_id=brand.id),
            required_permission='admin.access',
        ),
        MoreItem(
            label=gettext('Brand Snippets'),
            icon='snippet',
            url=url_for(
                'snippet_admin.index_for_scope',
                scope_type='brand',
                scope_name=brand.id,
            ),
            required_permission='snippet.view',
        ),
        MoreItem(
            label=gettext('Required Consents'),
            icon='consent',
            url=url_for('consent_admin.requirement_index', brand_id=brand.id),
            required_permission='consent.administrate',
        ),
    ]


def get_party_items(party: Party) -> list[MoreItem]:
    return [
        MoreItem(
            label=gettext('Guest Servers'),
            icon='server',
            url=url_for('guest_server_admin.server_index', party_id=party.id),
            required_permission='guest_server.view',
        ),
        MoreItem(
            label=gettext('Organizer Presence'),
            icon='date-okay',
            url=url_for('orga_presence.view', party_id=party.id),
            required_permission='orga_presence.view',
        ),
        MoreItem(
            label=gettext('Paid Products Report'),
            icon='shop-order',
            url=url_for(
                'shop_paid_products_report_admin.index', party_id=party.id
            ),
            required_permission='shop_order.view',
        ),
        MoreItem(
            label=gettext('Timetable'),
            icon='date',
            url=url_for('timetable_admin.view', party_id=party.id),
            required_permission='timetable.update',
        ),
        MoreItem(
            label=gettext('Tournaments'),
            icon='trophy',
            url=url_for('tourney_tourney_admin.index', party_id=party.id),
            required_permission='tourney.view',
        ),
    ]


def get_site_items(site: Site) -> list[MoreItem]:
    return [
        MoreItem(
            label=gettext('Discussion Board'),
            icon='board',
            url=url_for('board_admin.board_view', board_id=site.board_id)
            if site.board_id
            else '',
            required_permission='board_category.view',
            precondition=site.board_id is not None,
        ),
    ]
