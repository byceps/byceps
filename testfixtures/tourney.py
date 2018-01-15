"""
testfixtures.tourney
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.tourney.models.match import Match


def create_match():
    return Match()
