"""Import seats from JSON lines.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from typing import Iterable

import click
from flask.cli import with_appcontext

from ...services.seating.seat_import_service import SeatToImport
from ...services.seating import seat_import_service
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
    with data_file.open() as f:
        lines = iter(f)
        parse_result = _parse_seats(party_id, lines)

    if parse_result.is_err():
        erroneous_line_numbers = parse_result.unwrap_err()
        line_numbers_str = ', '.join(map(str, sorted(erroneous_line_numbers)))
        click.secho(
            '\nNot attempting actual importing of seats due to parsing errors '
            f'in these lines: {line_numbers_str}',
            fg='red',
        )
        return

    line_numbers_and_seats_to_import = parse_result.unwrap()
    _import_seats(line_numbers_and_seats_to_import)


def _parse_seats(
    party_id: PartyID, lines: Iterable[str]
) -> Result[list[tuple[int, SeatToImport]], set[int]]:
    line_numbers_and_seats_to_import: list[tuple[int, SeatToImport]] = []
    erroneous_line_numbers = set()

    loaded_seats = seat_import_service.load_seats_from_json_lines(
        party_id, lines
    )
    for line_number, parse_result in loaded_seats:
        if parse_result.is_err():
            erroneous_line_numbers.add(line_number)

            error_str = parse_result.unwrap_err()
            click.secho(f'[line {line_number}] {error_str}', fg='red')

            continue

        seat_to_import = parse_result.unwrap()

        line_numbers_and_seats_to_import.append((line_number, seat_to_import))

    if erroneous_line_numbers:
        return Err(erroneous_line_numbers)

    return Ok(line_numbers_and_seats_to_import)


def _import_seats(
    line_numbers_and_seats_to_import: list[tuple[int, SeatToImport]]
) -> None:
    """Import seats into database."""
    for line_number, seat_to_import in line_numbers_and_seats_to_import:
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
