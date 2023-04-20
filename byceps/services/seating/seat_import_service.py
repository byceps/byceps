"""
byceps.services.seating.seat_import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
import json
from typing import Optional

from pydantic import ValidationError

from byceps.services.ticketing import ticket_category_service
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.typing import PartyID
from byceps.util.result import Err, Ok, Result

from . import seat_group_service, seat_service, seating_area_service
from .models import Seat, SeatingAreaID, SeatToImport, SerializableSeatToImport


def serialize_seat_to_import(
    area_title: str,
    coord_x: int,
    coord_y: int,
    category_title: str,
    rotation: Optional[int] = None,
    label: Optional[str] = None,
    type_: Optional[str] = None,
    group_title: Optional[str] = None,
) -> str:
    """Serialize a seat to JSON so it can be imported."""
    model = SerializableSeatToImport(
        area_title=area_title,
        coord_x=coord_x,
        coord_y=coord_y,
        category_title=category_title,
    )

    if rotation is not None:
        model.rotation = rotation

    if label is not None:
        model.label = label

    if type_ is not None:
        model.type_ = type_

    if group_title is not None:
        model.group_title = group_title

    return model.json(exclude_unset=True)


def load_seats_from_json_lines(
    party_id: PartyID, lines: Iterable[str]
) -> Iterator[tuple[int, Result[SeatToImport, str]]]:
    parser = _create_parser(party_id)
    return parser.parse_lines(lines)


def _create_parser(party_id: PartyID) -> _SeatsImportParser:
    """Create a parser, populated with party-specific data."""
    area_ids_by_title = _get_area_ids_by_title(party_id)
    category_ids_by_title = _get_category_ids_by_title(party_id)
    seat_group_titles = _get_seat_group_titles(party_id)

    return _SeatsImportParser(
        area_ids_by_title, category_ids_by_title, seat_group_titles
    )


def _get_area_ids_by_title(party_id: PartyID) -> dict[str, SeatingAreaID]:
    """Get the party's seating areas as a mapping from title to ID."""
    areas = seating_area_service.get_areas_for_party(party_id)
    return {area.title: area.id for area in areas}


def _get_category_ids_by_title(
    party_id: PartyID,
) -> dict[str, TicketCategoryID]:
    """Get the party's ticket categories as a mapping from title to ID."""
    categories = ticket_category_service.get_categories_for_party(party_id)
    return {category.title: category.id for category in categories}


def _get_seat_group_titles(party_id: PartyID) -> set[str]:
    """Get the party's seat groups' titles."""
    groups = seat_group_service.get_all_seat_groups_for_party(party_id)
    return {group.title for group in groups}


class _SeatsImportParser:
    """Parse JSON Lines records into importable seat objects."""

    def __init__(
        self,
        area_ids_by_title: dict[str, SeatingAreaID],
        category_ids_by_title: dict[str, TicketCategoryID],
        seat_group_titles: set[str],
    ) -> None:
        self._area_ids_by_title = area_ids_by_title
        self._category_ids_by_title = category_ids_by_title
        self._seat_group_titles = seat_group_titles

    def parse_lines(
        self, lines: Iterable[str]
    ) -> Iterator[tuple[int, Result[SeatToImport, str]]]:
        """Parse JSON lines into importable seat objects."""
        for line_number, line in enumerate(lines, start=1):
            parse_result = self._parse_line(line.rstrip())
            yield line_number, parse_result

    def _parse_line(self, line: str) -> Result[SeatToImport, str]:
        """Parse a JSON line into an importable seat object."""
        parse_result = _parse_seat_json(line)
        return parse_result.and_then(self._assemble_seat_to_import)

    def _assemble_seat_to_import(
        self, parsed_seat: SerializableSeatToImport
    ) -> Result[SeatToImport, str]:
        """Build seat object to import by setting area and category IDs."""
        area_title = parsed_seat.area_title
        area_id = self._area_ids_by_title.get(area_title)
        if area_id is None:
            return Err(f'Unknown area title "{area_title}"')

        category_title = parsed_seat.category_title
        category_id = self._category_ids_by_title.get(category_title)
        if category_id is None:
            return Err(f'Unknown category title "{category_title}"')

        group_title = parsed_seat.group_title
        if group_title in self._seat_group_titles:
            return Err(f'Seat group with title "{group_title}" already exists')

        assembled_seat = SeatToImport(
            area_id=area_id,
            coord_x=parsed_seat.coord_x,
            coord_y=parsed_seat.coord_y,
            category_id=category_id,
            rotation=parsed_seat.rotation,
            label=parsed_seat.label,
            type_=parsed_seat.type_,
            group_title=parsed_seat.group_title,
        )
        return Ok(assembled_seat)


def _parse_seat_json(json_data: str) -> Result[SerializableSeatToImport, str]:
    """Parse a JSON object into a seat import object."""
    try:
        data_dict = json.loads(json_data)
    except json.decoder.JSONDecodeError as e:
        return Err(f'Could not parse JSON: {e}')

    try:
        seat_to_import = SerializableSeatToImport.parse_obj(data_dict)
        return Ok(seat_to_import)
    except ValidationError as e:
        return Err(str(e))


def import_seat(seat_to_import: SeatToImport) -> Result[Seat, str]:
    """Import a seat."""
    try:
        imported_seat = seat_service.create_seat(
            seat_to_import.area_id,
            seat_to_import.coord_x,
            seat_to_import.coord_y,
            seat_to_import.category_id,
            rotation=seat_to_import.rotation,
            label=seat_to_import.label,
            type_=seat_to_import.type_,
        )
        return Ok(imported_seat)
    except Exception as e:
        return Err(str(e))
