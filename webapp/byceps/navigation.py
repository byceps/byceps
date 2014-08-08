# -*- coding: utf-8 -*-

"""
byceps.navigation
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from .blueprints.contentpage_admin.authorization import ContentPagePermission
from .blueprints.party_admin.authorization import PartyPermission
from .blueprints.user_admin.authorization import UserPermission
from .util.navigation import Navigation, NavigationItem


navigation = Navigation()
navigation.add_item('user_admin.index', 'Benutzer', id='user', required_permission=UserPermission.list)
navigation.add_item('party_admin.index', 'Parties', id='party', required_permission=PartyPermission.list)
navigation.add_item('contentpage_admin.index', 'Seiten', id='contentpage', required_permission=ContentPagePermission.list)
