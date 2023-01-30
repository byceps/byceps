"""Import seats from JSON lines.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import click
from flask.cli import with_appcontext

from ...services.seating import seat_import_service, seating_area_service
from ...services.ticketing import ticket_category_service
from ...typing import PartyID


@click.command()
@click.argument('party_id')
@click.argument(
    'data_file', type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@with_appcontext
def import_seats(party_id: PartyID, data_file: Path) -> None:
    """Import seats."""
    areas = seating_area_service.get_areas_for_party(party_id)
    area_ids_by_title = {area.title: area.id for area in areas}

    categories = ticket_category_service.get_categories_for_party(party_id)
    category_ids_by_title = {
        category.title: category.id for category in categories
    }

    with data_file.open() as f:
        lines = seat_import_service.parse_lines(f)
        for line_number, line in enumerate(lines, start=1):
            try:
                seat_to_import = seat_import_service.parse_seat_json(line)
                seat = seat_import_service.import_seat(
                    seat_to_import, area_ids_by_title, category_ids_by_title
                )
                click.secho(
                    f'[line {line_number}] Imported seat '
                    f'(area="{seat_to_import.area_title}", x={seat.coord_x}, y={seat.coord_y}, category="{seat_to_import.category_title}").',
                    fg='green',
                )
            except Exception as e:
                click.secho(
                    f'[line {line_number}] Could not import seat: {e}', fg='red'
                )
