# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from blinker import Namespace


news_signals = Namespace()


item_published = news_signals.signal('item-published')
