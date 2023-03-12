"""Import seats from JSON lines.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import click
from flask.cli import with_appcontext

from ...services.seating.models import SeatingAreaID
from ...services.seating.seat_import_service import SeatToImport
from ...services.seating import seat_import_service, seating_area_service
from ...services.ticketing.models.ticket import TicketCategoryID
from ...services.ticketing import ticket_category_service
from ...typing import PartyID
from ...util.result import Err, Ok, Result


@click.command()
@click.argument('party_id')
@click.argument(
    'data_file', type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@with_appcontext
def import_seats(party_id: PartyID, data_file: Path) -> None:
    """Import seats."""
    area_ids_by_title = get_area_ids_by_title(party_id)
    category_ids_by_title = get_category_ids_by_title(party_id)

    seats_to_import_result = get_seats_to_import(
        data_file, area_ids_by_title, category_ids_by_title
    )

    if seats_to_import_result.is_err():
        erroneous_line_numbers = seats_to_import_result.unwrap_err()
        line_numbers_str = ', '.join(map(str, sorted(erroneous_line_numbers)))
        click.secho(
            '\nNot attempting actual importing of seats due to parsing errors '
            f'in these lines: {line_numbers_str}',
            fg='red',
        )
        return

    for line_number, seat_to_import in seats_to_import_result.unwrap():
        import_result = seat_import_service.import_seat(seat_to_import)

        if import_result.is_err():
            error_str = import_result.unwrap_err()
            click.secho(
                f'[line {line_number}] Import of seat failed: {error_str}',
                fg='red',
            )
            continue

        imported_seat = import_result.unwrap()
        click.secho(
            f'[line {line_number}] Imported seat '
            f'(area_id="{imported_seat.area_id}", x={imported_seat.coord_x}, y={imported_seat.coord_y}, category_id="{imported_seat.category_id}").',
            fg='green',
        )


def get_area_ids_by_title(party_id: PartyID) -> dict[str, SeatingAreaID]:
    """Get the party's seating areas as a mapping from title to ID."""
    areas = seating_area_service.get_areas_for_party(party_id)
    return {area.title: area.id for area in areas}


def get_category_ids_by_title(party_id: PartyID) -> dict[str, TicketCategoryID]:
    """Get the party's ticket categories as a mapping from title to ID."""
    categories = ticket_category_service.get_categories_for_party(party_id)
    return {category.title: category.id for category in categories}


def get_seats_to_import(
    data_file: Path,
    area_ids_by_title: dict[str, SeatingAreaID],
    category_ids_by_title: dict[str, TicketCategoryID],
) -> Result[list[tuple[int, SeatToImport]], set[int]]:
    """Obtain the seats to import."""
    line_numbers_and_seats_to_import: list[tuple[int, SeatToImport]] = []
    erroneous_line_numbers = set()

    with data_file.open() as f:
        lines = seat_import_service.parse_lines(f)
        for line_number, line in enumerate(lines, start=1):
            parse_result = seat_import_service.parse_seat_json(line)

            if parse_result.is_err():
                erroneous_line_numbers.add(line_number)

                error_str = parse_result.unwrap_err()
                click.secho(
                    f'[line {line_number}] Could not parse seat: {error_str}',
                    fg='red',
                )

                continue

            parsed_seat = parse_result.unwrap()

            assembly_result = seat_import_service.assemble_seat_to_import(
                parsed_seat, area_ids_by_title, category_ids_by_title
            )

            if assembly_result.is_err():
                erroneous_line_numbers.add(line_number)

                error_str = assembly_result.unwrap_err()
                click.secho(
                    f'[line {line_number}] Could not assemble seat: {error_str}',
                    fg='red',
                )

                continue

            seat_to_import = assembly_result.unwrap()

            line_numbers_and_seats_to_import.append(
                (line_number, seat_to_import)
            )

        if erroneous_line_numbers:
            return Err(erroneous_line_numbers)

        return Ok(line_numbers_and_seats_to_import)
