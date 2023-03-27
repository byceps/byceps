"""
byceps.blueprints.site.site.navigation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps
from typing import Optional

from flask import g

from ....services.site_navigation.models import NavMenuID
from ....services.site_navigation import site_navigation_service
from ....util.l10n import get_default_locale, get_locale_str


def find_subnav_menu_id(view_name: str) -> Optional[NavMenuID]:
    """Return the ID of the navigation submenu for the view."""
    language_code = get_locale_str() or get_default_locale()
    return site_navigation_service.find_submenu_id_for_view(
        g.site_id, language_code, view_name
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
