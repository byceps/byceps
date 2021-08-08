"""
byceps.blueprints.site.orga_team.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g

from ....services.orga_team import service as orga_team_service
from ....typing import UserID


def is_orga_for_current_party(user_id: UserID) -> bool:
    """Return `True` if a current party is set and the current user is
    an organizer for it.
    """
    if g.party_id is None:
        return False

    return orga_team_service.is_orga_for_party(user_id, g.party_id)
