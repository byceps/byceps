"""
byceps.services.tourney.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TourneyCategoryAlreadyAtBottomError:
    pass


@dataclass(frozen=True)
class TourneyCategoryAlreadyAtTopError:
    pass
