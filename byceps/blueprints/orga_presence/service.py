# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_presence.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Presence, Task


def get_presences(party_id):
    """Return all presences for that party."""
    return Presence.query \
        .for_party_id(party_id) \
        .options(db.joinedload('orga')) \
        .all()


def get_tasks(party_id):
    """Return all tasks for that party."""
    return Task.query \
        .for_party_id(party_id) \
        .all()
