"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.cli.commands.create_database_tables import _load_dbmodels
from byceps.database import db
from byceps.services.authz import authz_service
from byceps.services.authz.models import RoleID
from byceps.services.language import language_service


def set_up_database() -> None:
    # Learn about all tables to also drop old ones no longer
    # defined in models.
    db.reflect()

    db.drop_all()

    _load_dbmodels()
    db.create_all()


def populate_database() -> None:
    for code in 'en', 'de':
        language_service.create_language(code)

    authz_service.create_role(RoleID('board_user'), 'Board User')


def tear_down_database() -> None:
    db.reflect()
    db.session.remove()
    db.drop_all()
