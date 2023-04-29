"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.cli.commands.create_database_tables import _load_dbmodels
from byceps.database import db


def set_up_database() -> None:
    # Learn about all tables to also drop old ones no longer
    # defined in models.
    db.reflect()

    db.drop_all()

    _load_dbmodels()
    db.create_all()


def tear_down_database() -> None:
    db.session.remove()
    db.drop_all()
