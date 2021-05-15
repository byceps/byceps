"""
byceps.blueprints.site.orga_team.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from ....services.orga_team import service as orga_team_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('orga_team', __name__)


@blueprint.get('/')
@templated
def index():
    """List all organizers for the current party."""
    if g.party_id is None:
        # No party is configured for the current site.
        abort(404)

    orgas = orga_team_service.get_public_orgas_for_party(g.party_id)
    orgas = sorted(
        orgas,
        key=lambda orga: user_service.get_sort_key_for_screen_name(orga.user),
    )

    return {
        'orgas': orgas,
    }
