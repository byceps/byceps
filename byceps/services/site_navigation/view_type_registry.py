"""
byceps.services.site_navigation.view_type_registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from flask_babel import lazy_gettext

from byceps.util.iterables import find


@dataclass(frozen=True, kw_only=True)
class ViewType:
    name: str
    endpoint: str
    label: str
    current_page_id: str


_VIEW_TYPES = [
    ViewType(
        name='homepage',
        endpoint='homepage.index',
        label=lazy_gettext('Home page'),
        current_page_id='homepage',
    ),
    ViewType(
        name='news',
        endpoint='news.index',
        label=lazy_gettext('News'),
        current_page_id='news',
    ),
    ViewType(
        name='seating_plan',
        endpoint='seating.index',
        label=lazy_gettext('Seating plan'),
        current_page_id='seating',
    ),
    ViewType(
        name='attendees',
        endpoint='attendance.attendees',
        label=lazy_gettext('Attendees'),
        current_page_id='attendees',
    ),
    ViewType(
        name='shop',
        endpoint='shop_order.order_form',
        label=lazy_gettext('Shop'),
        current_page_id='shop_order',
    ),
    ViewType(
        name='board',
        endpoint='board.category_index',
        label=lazy_gettext('Board'),
        current_page_id='board',
    ),
    ViewType(
        name='orga_team',
        endpoint='orga_team.index',
        label=lazy_gettext('Orga team'),
        current_page_id='orga_team',
    ),
    ViewType(
        name='party_history',
        endpoint='party_history.index',
        label=lazy_gettext('Party history'),
        current_page_id='party_history',
    ),
    ViewType(
        name='timetable',
        endpoint='timetable.index',
        label=lazy_gettext('Timetable'),
        current_page_id='timetable',
    ),
    ViewType(
        name='gallery',
        endpoint='gallery.index',
        label=lazy_gettext('Galleries'),
        current_page_id='gallery',
    ),
]


def get_view_types() -> list[ViewType]:
    """Return the available view types."""
    return list(_VIEW_TYPES)


def find_view_type_by_name(name: str) -> ViewType | None:
    """Return the view type with that name, or `None` if not found."""
    return find(_VIEW_TYPES, lambda view_type: view_type.name == name)
