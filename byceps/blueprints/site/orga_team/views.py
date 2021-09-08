"""
byceps.blueprints.site.orga_team.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from typing import Iterable, Iterator

from flask import abort, g

from ....services.orga_team import service as orga_team_service
from ....services.orga_team.transfer.models import PublicOrga
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
    orgas = _merge_public_orgas(orgas)
    orgas = sorted(
        orgas,
        key=lambda orga: user_service.get_sort_key_for_screen_name(orga.user),
    )

    return {
        'orgas': orgas,
    }


def _merge_public_orgas(
    public_orgas: Iterable[PublicOrga],
) -> Iterator[PublicOrga]:
    """Merge team names and duties of public orga objects that represent
    the same person.
    """
    orgas_by_user_id = defaultdict(list)
    for orga in public_orgas:
        orgas_by_user_id[orga.user.id].append(orga)

    for _, orgas in orgas_by_user_id.items():
        first = orgas[0]
        if len(orgas) > 1:
            team_names = ', '.join(orga.team_name for orga in orgas)
            duties = ', '.join(orga.duties for orga in orgas if orga.duties)
            yield PublicOrga(
                user=first.user,
                full_name=first.full_name,
                team_name=team_names,
                duties=duties,
            )
        else:
            yield first
