"""
byceps.services.site.blueprints.site.navigation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps

from flask import g

from byceps.services.site_navigation import site_navigation_service
from byceps.services.site_navigation.models import NavMenuID
from byceps.util.l10n import get_default_locale, get_locale_str


def find_subnav_menu_id(view_name: str) -> NavMenuID | None:
    """Return the ID of the navigation submenu for the view."""
    language_code = get_locale_str() or get_default_locale()
    return site_navigation_service.find_submenu_id_for_view(
        g.site.id, language_code, view_name
    )


def subnavigation_for_view(view_name: str):
    """Decorator to render navigation submenu for this view, if defined."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = func(*args, **kwargs)
            if isinstance(context, dict):
                context['subnav_menu_id'] = find_subnav_menu_id(view_name)
            return context

        return wrapper

    return decorator
