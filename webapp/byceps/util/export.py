# -*- coding: utf-8 -*-

"""
byceps.util.export
~~~~~~~~~~~~~~~~~~

Data export as CSV.

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

import csv
import io


def serialize_to_csv(field_names, rows):
    """Serialize the rows (must be dictionary objects) to CSV."""
    with io.StringIO(newline='') as f:
        writer = csv.DictWriter(f, field_names,
                                dialect=csv.excel,
                                delimiter=';')

        writer.writeheader()
        writer.writerows(rows)

        f.seek(0)
        yield from f
