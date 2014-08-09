# -*- coding: utf-8 -*-

"""
byceps.blueprints.orgateam.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    users = association_proxy('associated_users', 'user')

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('title') \
            .build()


class OrgaTeamUser(db.Model):
    """The assignment of a user to an orga team."""
    __tablename__ = 'orga_team_users'

    orga_team_id = db.Column(db.Unicode(40), db.ForeignKey('orga_teams.id'), primary_key=True)
    orga_team = db.relationship(OrgaTeam, collection_class=set)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, backref='associated_users', collection_class=set)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('orga_team') \
            .add_with_lookup('user') \
            .build()
