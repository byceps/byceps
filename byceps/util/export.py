"""
byceps.util.export
~~~~~~~~~~~~~~~~~~

Data export as CSV.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import csv
import io
from typing import Dict, Iterator, Sequence


def serialize_to_csv(
    field_names: Sequence[str], rows: Sequence[Dict[str, str]]
) -> Iterator[str]:
    """Serialize the rows (must be dictionary objects) to CSV."""
    with io.StringIO(newline='') as f:
        writer = csv.DictWriter(
            f, field_names, dialect=csv.excel, delimiter=';'
        )

        writer.writeheader()
        writer.writerows(rows)

        f.seek(0)
        yield from f
