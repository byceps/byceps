"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.seating import seat_import_service


@pytest.mark.parametrize(
    (
        'area_title',
        'coord_x',
        'coord_y',
        'category_title',
        'rotation',
        'label',
        'type_',
        'group_title',
        'expected',
    ),
    [
        (
            'Main hall',
            23,
            42,
            'Standard',
            None,
            None,
            None,
            None,
            '{"area_title":"Main hall","coord_x":23,"coord_y":42,"category_title":"Standard"}',
        ),
        (
            'Second hall',
            10,
            25,
            'VIP',
            45,
            'VIP Seat 7',
            'vip',
            'VIPs Group #1',
            '{"area_title":"Second hall","coord_x":10,"coord_y":25,"category_title":"VIP","rotation":45,"label":"VIP Seat 7","type":"vip","group_title":"VIPs Group #1"}',
        ),
    ],
)
def test_serialize_seat_to_import(
    area_title: str,
    coord_x: int,
    coord_y: int,
    category_title: str,
    rotation: int | None,
    label: str | None,
    type_: str | None,
    group_title: str | None,
    expected: str,
):
    actual = seat_import_service.serialize_seat_to_import(
        area_title,
        coord_x,
        coord_y,
        category_title,
        rotation,
        label,
        type_,
        group_title,
    )

    assert actual == expected
