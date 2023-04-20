"""
byceps.services.tourney.dbmodels.match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db, generate_uuid7


class DbMatch(db.Model):
    """A match between two opponents."""

    __tablename__ = 'tourney_matches'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
