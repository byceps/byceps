# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...config import get_current_party_id
from ...services.party import service as party_service
from ...services.ticket import service as ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.templating import templated


blueprint = create_blueprint('party', __name__)


@blueprint.before_app_request
def before_request():
    party_id = get_current_party_id()

    party = party_service.find_party_with_brand(party_id)

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
    archived_parties = party_service.get_archived_parties()
    attendees_by_party = ticket_service.get_attendees_by_party(archived_parties)

    return {
        'parties': archived_parties,
        'attendees_by_party': attendees_by_party,
    }
