# -*- coding: utf-8 -*-

from byceps.blueprints.orga_admin.authorization import OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.snippet_admin.authorization import SnippetPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.util.navigation import Navigation, NavigationItem


navigation = Navigation()
navigation.add_item('user_admin.index', 'Benutzer', id='user', required_permission=UserPermission.list)
navigation.add_item('party_admin.index', 'Parties', id='party', required_permission=PartyPermission.list)
navigation.add_item('snippet_admin.index', 'Snippets', id='snippet', required_permission=SnippetPermission.list)
navigation.add_item('orga_admin.index', 'Orgateams', id='orgateam', required_permission=OrgaTeamPermission.list)
navigation.add_item('orga.index', 'Orgas', id='orga')
navigation.add_item('seating.index', 'Sitzplan', id='seating')
