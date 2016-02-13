# -*- coding: utf-8 -*-

"""
testfixtures.tourney
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.tourney.models.match import Match


def create_match():
    return Match()
