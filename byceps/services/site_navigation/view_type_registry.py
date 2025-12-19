"""
byceps.services.site_navigation.view_type_registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
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
        name=name,
        endpoint=endpoint,
        label=label,
        current_page_id=current_page_id,
    )
    for name, endpoint, label, current_page_id in [
        ('homepage', 'homepage.index', lazy_gettext('Home page'), 'homepage'),
        ('news', 'news.index', lazy_gettext('News'), 'news'),
        (
            'seating_plan',
            'seating.index',
            lazy_gettext('Seating plan'),
            'seating',
        ),
        (
            'attendees',
            'attendance.attendees',
            lazy_gettext('Attendees'),
            'attendees',
        ),
        ('shop', 'shop_order.order_form', lazy_gettext('Shop'), 'shop_order'),
        ('board', 'board.category_index', lazy_gettext('Board'), 'board'),
        (
            'orga_team',
            'orga_team.index',
            lazy_gettext('Orga team'),
            'orga_team',
        ),
        (
            'party_history',
            'party_history.index',
            lazy_gettext('Party history'),
            'party_history',
        ),
        (
            'timetable',
            'timetable.index',
            lazy_gettext('Timetable'),
            'timetable',
        ),
        ('gallery', 'gallery.index', lazy_gettext('Galleries'), 'gallery'),
    ]
]


def get_view_types() -> list[ViewType]:
    """Return the available view types."""
    return list(_VIEW_TYPES)


def find_view_type_by_name(name: str) -> ViewType | None:
    """Return the view type with that name, or `None` if not found."""
    return find(_VIEW_TYPES, lambda view_type: view_type.name == name)
