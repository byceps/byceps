"""
byceps.services.site.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g, url_for

from byceps.services.page.blueprints.site.templating import url_for_site_page
from byceps.services.site_navigation import site_navigation_service
from byceps.services.site_navigation.models import (
    NavItem,
    NavItemForRendering,
    NavItemTargetType,
    NavMenuID,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.l10n import get_locale_str


blueprint = create_blueprint('site', __name__)


@blueprint.app_template_global()
def get_nav_menu_items(menu_name: str) -> list[NavItemForRendering]:
    """Make navigation menus accessible to templates."""
    locale_str = get_locale_str()
    if locale_str is None:  # outside of request
        return []

    items = site_navigation_service.get_items_for_menu(
        g.site_id, menu_name, locale_str
    )
    return _to_items_for_rendering(g.site_id, items)


@blueprint.app_template_global()
def get_nav_menu_items_for_menu_id(
    menu_id: NavMenuID,
) -> list[NavItemForRendering]:
    """Make navigation menus accessible to templates."""
    items = site_navigation_service.get_items_for_menu_id(menu_id)
    return _to_items_for_rendering(g.site_id, items)


def _to_items_for_rendering(
    site_id: str, items: list[NavItem]
) -> list[NavItemForRendering]:
    return [_to_item_for_rendering(site_id, item) for item in items]


def _to_item_for_rendering(site_id: str, item: NavItem) -> NavItemForRendering:
    target = _assemble_target(site_id, item)

    return NavItemForRendering(
        target=target,
        label=item.label,
        current_page_id=item.current_page_id,
        children=[],
    )


def _assemble_target(site_id: str, item: NavItem) -> str:
    match item.target_type:
        case NavItemTargetType.endpoint:
            return url_for(item.target)

        case NavItemTargetType.page:
            return url_for_site_page(site_id, item.target)

        case NavItemTargetType.url:
            return item.target

        case NavItemTargetType.view:
            view_type = site_navigation_service.find_view_type_by_name(
                item.target
            )
            if not view_type:
                raise ValueError('Unknown view type')

            return url_for(view_type.endpoint)

        case _:
            raise ValueError('Unknown target type')
