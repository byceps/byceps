"""
byceps.services.tourney.models.match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db, generate_uuid


class Match(db.Model):
    """A match between two opponents."""

    __tablename__ = 'tourney_matches'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
