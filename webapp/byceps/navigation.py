# -*- coding: utf-8 -*-

"""
byceps.navigation
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from .util.navigation import Navigation, NavigationItem


navigation = Navigation()
navigation.add_item('user_admin.index', 'Benutzer', id='user')
navigation.add_item('party_admin.index', 'Parties', id='party')
navigation.add_item('contentpage_admin.index', 'Seiten', id='contentpage')
