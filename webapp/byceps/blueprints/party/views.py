# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...config import get_current_party_id
from ...database import db
from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import Party
from . import service


blueprint = create_blueprint('party', __name__)


@blueprint.before_app_request
def before_request():
    id = get_current_party_id()
    party = get_party(id)
    if party is None:
        raise Exception('Unknown party ID "{}".'.format(id))

    g.party = party


def get_party(id):
    return Party.query \
        .options(db.joinedload('brand')) \
        .get(id)


@blueprint.route('/info')
@templated
def info():
    """Show information about the current party."""


@blueprint.route('/archive')
@templated
def archive():
    """Show archived parties."""
    archived_parties = service.get_archived_parties()
    attendee_screen_names_by_party \
        = service.get_attendee_screen_names_by_party(archived_parties)

    return {
        'parties': archived_parties,
        'attendee_screen_names_by_party': attendee_screen_names_by_party,
    }
