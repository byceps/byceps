# -*- coding: utf-8 -*-

"""
byceps.blueprints.tourney.models.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import BaseQuery, db, generate_uuid

from ....util.instances import ReprBuilder

from .tourney_category import TourneyCategory


class Tourney(db.Model):
    """A tournament."""
    __tablename__ = 'tourney_teams'
    __table_args__ = (
        db.UniqueConstraint('group_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    group_id = db.Column(db.Uuid, db.ForeignKey('tourney_groups.id'), index=True, nullable=False)
    group = db.relationship(TourneyCategory)
    title = db.Column(db.Unicode(40), nullable=False)

    def __init__(self, group, title):
        self.group = group
        self.title = title

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('group') \
            .add_with_lookup('title') \
            .build()
