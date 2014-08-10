# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from sqlalchemy.ext.associationproxy import association_proxy

from ...database import db
from ...util.instances import ReprBuilder

from ..user.models import User


class OrgaTeam(db.Model):
    """A group of organizers."""
    __tablename__ = 'orga_teams'

    id = db.Column(db.Unicode(40), primary_key=True)
    title = db.Column(db.Unicode(40), unique=True)

    members = association_proxy('associated_users', 'user')

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('title') \
            .add_custom('{:d} members'.format(len(self.members))) \
            .build()


class Membership(db.Model):
    """The assignment of a user to an organizer team."""
    __tablename__ = 'orga_team_memberships'

    orga_team_id = db.Column(db.Unicode(40), db.ForeignKey('orga_teams.id'), primary_key=True)
    orga_team = db.relationship(OrgaTeam, collection_class=set, backref='associated_users')
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, collection_class=set)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('orga_team') \
            .add_with_lookup('user') \
            .build()


def get_orgas():
    memberships = Membership.query.all()
    for m in memberships:
        yield m.user
