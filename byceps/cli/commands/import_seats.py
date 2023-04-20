"""Import seats from JSON lines.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

import click
from flask.cli import with_appcontext

from byceps.services.seating import seat_group_service, seat_import_service
from byceps.services.seating.models import Seat
from byceps.services.seating.seat_import_service import SeatToImport
from byceps.typing import PartyID
from byceps.util.result import Err, Ok, Result


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
    imported_seats_and_group_titles = list(
        _import_seats(line_numbers_and_seats_to_import)
    )
    _import_seat_groups(party_id, imported_seats_and_group_titles)


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
) -> Iterator[tuple[Seat, str | None]]:
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

        yield imported_seat, seat_to_import.group_title


def _import_seat_groups(
    party_id: PartyID, seats_and_group_titles: list[tuple[Seat, str | None]]
) -> None:
    """Import seat groups into database."""
    seats_by_group_title = defaultdict(list)

    for seat, group_title in seats_and_group_titles:
        if group_title is not None:
            seats_by_group_title[group_title].append(seat)

    for group_title, seats in seats_by_group_title.items():
        db_group = seat_group_service.create_seat_group(
            party_id, seats[0].category_id, group_title, seats
        )

        click.secho(
            f'Imported seat group "{db_group.title}" with {db_group.seat_quantity} seats (category_id="{db_group.ticket_category_id}")',
            fg='green',
        )
