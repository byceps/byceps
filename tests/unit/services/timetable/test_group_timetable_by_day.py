"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime

from byceps.services.party.models import PartyID
from byceps.services.timetable import timetable_service
from byceps.services.timetable.models import (
    Timetable,
    TimetableGroupedByDay,
    TimetableID,
    TimetableItem,
    TimetableItemID,
)

from tests.helpers import generate_uuid


def test_group_timetable_items_by_day():
    timetable_id = TimetableID(generate_uuid())
    party_id = PartyID('acmecon-2024')

    item1 = _build_item(timetable_id, datetime(2024, 9, 20, 22, 0, 0))
    item2 = _build_item(timetable_id, datetime(2024, 9, 21, 16, 0, 0))
    item3 = _build_item(timetable_id, datetime(2024, 9, 21, 18, 0, 0))
    item4 = _build_item(timetable_id, datetime(2024, 9, 22, 11, 0, 0))

    expected = TimetableGroupedByDay(
        id=timetable_id,
        party_id=party_id,
        hidden=False,
        items=[
            (date(2024, 9, 20), [item1]),
            (date(2024, 9, 21), [item2, item3]),
            (date(2024, 9, 22), [item4]),
        ],
    )

    timetable = _build_timetable(
        timetable_id, party_id, [item1, item2, item3, item4]
    )

    assert timetable_service.group_timetable_items_by_day(timetable) == expected


def _build_timetable(
    timetable_id: TimetableID, party_id: PartyID, items: list[TimetableItem]
) -> Timetable:
    return Timetable(
        id=timetable_id,
        party_id=party_id,
        hidden=False,
        items=items,
    )


def _build_item(
    timetable_id: TimetableID, scheduled_at: datetime
) -> TimetableItem:
    return TimetableItem(
        id=TimetableItemID(generate_uuid()),
        timetable_id=timetable_id,
        scheduled_at=scheduled_at,
        description='Item',
        location=None,
        link_target=None,
        link_label=None,
        hidden=False,
    )
