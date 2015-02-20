# -*- coding: utf-8 -*-

from byceps.util.navigation import Navigation, NavigationItem


info = Navigation('Informationen')
info.add_item('news.index', 'Neuigkeiten', id='news')
info.add_item('party.info', 'Partydetails', id='party')
info.add_item('orga.index', 'Team', id='orga')
#info.add_item('user_group.index', 'Benutzergruppen', id='user_group')
info.add_item('seating.index', 'Sitzplan', id='seating')
info.add_item('terms.view_current', 'AGB', id='terms')
info.add_item('board.category_index', 'Forum', id='board')


def get_blocks():
    return [info]
