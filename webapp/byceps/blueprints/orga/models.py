# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from operator import attrgetter

from flask import g
from sqlalchemy.ext.associationproxy import association_proxy

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..party.models import Party
from ..user.models import User


class OrgaFlag(db.Model):
    """A user's organizer status for a single brand."""
    __tablename__ = 'orga_flags'

    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    brand = db.relationship(Brand)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, backref='orga_flags')

    def __repr__(self):
        return ReprBuilder(self) \
            .add('brand', self.brand.title) \
            .add('user', self.user.screen_name) \
            .build()


class OrgaTeam(db.Model):
    """A group of organizers."""
    __tablename__ = 'orga_teams'

    id = db.Column(db.Unicode(40), primary_key=True)
    title = db.Column(db.Unicode(40), unique=True)

    members = association_proxy('memberships', 'user')

    @property
    def members_for_current_party(self):
        current_party_memberships = filter(lambda m: m.belongs_to_current_party,
                                           self.memberships)
        return list(map(attrgetter('user'), current_party_memberships))

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('title') \
            .add_custom('{:d} members'.format(len(self.members))) \
            .build()


class MembershipQuery(BaseQuery):

    def for_current_party(self):
        return self.filter_by(party_id=g.party.id)


class Membership(db.Model):
    """The assignment of a user to an organizer team."""
    __tablename__ = 'orga_team_memberships'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'user_id'),
    )
    query_class = MembershipQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    orga_team_id = db.Column(db.Unicode(40), db.ForeignKey('orga_teams.id'))
    orga_team = db.relationship(OrgaTeam, collection_class=set, backref='memberships')
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'))
    party = db.relationship(Party)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    user = db.relationship(User, collection_class=set, backref='orga_team_memberships')

    @property
    def belongs_to_current_party(self):
        return self.party == g.party

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('orga_team') \
            .add_with_lookup('party') \
            .add_with_lookup('user') \
            .build()


def get_orgas_for_current_party():
    memberships = Membership.query.for_current_party().all()
    for m in memberships:
        yield m.user
