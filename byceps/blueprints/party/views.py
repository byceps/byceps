"""
byceps.blueprints.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...config import get_current_party_id
from ...services.party import service as party_service
from ...services.ticketing import attendance_service
from ...util.framework.blueprint import create_blueprint
from ...util.templating import templated


blueprint = create_blueprint('party', __name__)


@blueprint.before_app_request
def before_request():
    party_id = get_current_party_id()

    party = party_service.find_party(party_id)

    if party is None:
        raise Exception('Unknown party ID "{}".'.format(party_id))

    g.party = party


@blueprint.route('/info')
@templated
def info():
    """Show information about the current party."""


@blueprint.route('/archive')
@templated
def archive():
    """Show archived parties."""
    brand_id = g.party.brand_id
    archived_parties = party_service.get_archived_parties_for_brand(brand_id)

    party_ids = {party.id for party in archived_parties}
    attendees_by_party_id = attendance_service.get_attendees_by_party(party_ids)

    return {
        'parties': archived_parties,
        'attendees_by_party_id': attendees_by_party_id,
    }
