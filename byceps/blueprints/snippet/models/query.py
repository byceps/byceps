# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet.models.query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import BaseQuery


class BelongsToPartyQuery(BaseQuery):

    def for_party(self, party):
        return self.for_party_with_id(party.id)

    def for_party_with_id(self, party_id):
        return self.filter_by(party_id=party_id)
