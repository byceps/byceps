"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from uuid import UUID

import pytest

from byceps.services.seating.seat_import_service import SeatsImportParser
from byceps.services.seating.models import SeatingAreaID, SeatToImport
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.util.result import Ok, Result


def seating_area_id(value: str) -> SeatingAreaID:
    return SeatingAreaID(UUID(value))


def ticket_category_id(value: str) -> TicketCategoryID:
    return TicketCategoryID(UUID(value))


@pytest.mark.parametrize(
    (
        'lines',
        'expected',
    ),
    [
        (
            [
                '{"area_title":"Main hall","coord_x":23,"coord_y":42,"category_title":"Standard"}',
                '{"area_title":"Second hall","coord_x":10,"coord_y":25,"category_title":"VIP","rotation":45,"label":"VIP Seat 7","type":"vip","blocked":true,"group_title":"VIPs Group #1"}',
            ],
            [
                (
                    1,
                    Ok(
                        SeatToImport(
                            area_id=seating_area_id(
                                '44101739-835b-4abe-a6f8-aab6469cf56d'
                            ),
                            coord_x=23,
                            coord_y=42,
                            category_id=ticket_category_id(
                                'a9a24cbb-4801-4b54-85dc-d3875ea8040d'
                            ),
                            rotation=None,
                            label=None,
                            type_=None,
                            blocked=False,
                            group_title=None,
                        ),
                    ),
                ),
                (
                    2,
                    Ok(
                        SeatToImport(
                            area_id=seating_area_id(
                                '774f971d-69a4-4cd9-a587-c7ed2f37dd89'
                            ),
                            coord_x=10,
                            coord_y=25,
                            category_id=ticket_category_id(
                                'cb3974d7-0e8d-40a1-8367-3a6493130a1c'
                            ),
                            rotation=45,
                            label='VIP Seat 7',
                            type_='vip',
                            blocked=True,
                            group_title='VIPs Group #1',
                        ),
                    ),
                ),
            ],
        ),
    ],
)
def test_seats_import_parser(
    lines: Iterable[str],
    expected: list[tuple[int, Result[SeatToImport, str]]],
):
    area_ids_by_title: dict[str, SeatingAreaID] = {
        'Main hall': seating_area_id('44101739-835b-4abe-a6f8-aab6469cf56d'),
        'Second hall': seating_area_id('774f971d-69a4-4cd9-a587-c7ed2f37dd89'),
    }

    category_ids_by_title: dict[str, TicketCategoryID] = {
        'Standard': ticket_category_id('a9a24cbb-4801-4b54-85dc-d3875ea8040d'),
        'VIP': ticket_category_id('cb3974d7-0e8d-40a1-8367-3a6493130a1c'),
    }

    seat_group_titles: set[str] = set()

    parser = SeatsImportParser(
        area_ids_by_title, category_ids_by_title, seat_group_titles
    )

    assert list(parser.parse_lines(lines)) == expected
