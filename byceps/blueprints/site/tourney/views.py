"""
byceps.blueprints.site.tourney.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
import dataclasses

from flask import abort, g

from ....services.party import service as party_service
from ....services.tourney import (
    category_service,
    participant_service,
    tourney_service,
)
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated


blueprint = create_blueprint('tourney', __name__)


@blueprint.get('/tourneys')
@templated
def tourney_index():
    """List all tournaments for the current party."""
    if g.party_id is None:
        # No party is configured for the current site.
        abort(404)

    party = party_service.find_party(g.party_id)
    if not party:
        abort(404)

    categories = category_service.get_categories_for_party(party.id)
    tourneys = tourney_service.get_tourneys_for_party(party.id)

    categories_with_tourneys = get_categories_with_tourneys(
        categories, tourneys
    )

    return {
        'categories_with_tourneys': categories_with_tourneys,
    }


def get_categories_with_tourneys(categories, tourneys):
    categories.sort(key=lambda c: c.position)
    tourneys.sort(key=lambda t: t.title)

    tourneys_by_category_id = defaultdict(list)
    for tourney in tourneys:
        tourneys_by_category_id[tourney.category_id].append(tourney)

    categories_with_tourneys = []
    for category in categories:
        tourneys_in_category = tourneys_by_category_id[category.id]
        if tourneys_in_category:
            categories_with_tourneys.append((category, tourneys_in_category))

    return categories_with_tourneys


@blueprint.get('/tourneys/<tourney_id>')
@templated
def tourney_view(tourney_id):
    """Show the tournament."""
    tourney = tourney_service.find_tourney(tourney_id)
    if not tourney:
        abort(404)

    participants = participant_service.get_participants_for_tourney(tourney.id)

    tourney = dataclasses.replace(
        tourney, current_participant_count=len(participants)
    )

    return {
        'tourney': tourney,
        'participants': participants,
    }
