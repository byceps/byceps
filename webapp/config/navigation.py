# -*- coding: utf-8 -*-

from byceps.blueprints.contentpage_admin.authorization import ContentPagePermission
from byceps.blueprints.orga_admin.authorization import OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.util.navigation import Navigation, NavigationItem


navigation = Navigation()
navigation.add_item('user_admin.index', 'Benutzer', id='user', required_permission=UserPermission.list)
navigation.add_item('party_admin.index', 'Parties', id='party', required_permission=PartyPermission.list)
navigation.add_item('contentpage_admin.index', 'Seiten', id='contentpage', required_permission=ContentPagePermission.list)
navigation.add_item('orga_admin.index', 'Orgateams', id='orgateam', required_permission=OrgaTeamPermission.list)
navigation.add_item('orga.index', 'Orgas', id='orga')
navigation.add_item('seating.index', 'Sitzplan', id='seating')
