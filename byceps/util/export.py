"""
byceps.util.export
~~~~~~~~~~~~~~~~~~

Data export as CSV.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator, Sequence
import csv
import io


def serialize_dicts_to_csv(
    field_names: Sequence[str],
    rows: Sequence[dict[str, str]],
    *,
    delimiter=',',
) -> Iterator[str]:
    """Serialize the rows (must be dictionary objects) to CSV."""
    with io.StringIO(newline='') as f:
        writer = csv.DictWriter(
            f, field_names, dialect=csv.excel, delimiter=delimiter
        )

        writer.writeheader()
        writer.writerows(rows)

        f.seek(0)
        yield from f


def serialize_tuples_to_csv(
    rows: Sequence[tuple[str, ...]],
    *,
    delimiter=',',
) -> Iterator[str]:
    """Serialize the rows (must be tuples) to CSV."""
    with io.StringIO(newline='') as f:
        writer = csv.writer(f, delimiter=delimiter)

        writer.writerows(rows)

        f.seek(0)
        yield from f
