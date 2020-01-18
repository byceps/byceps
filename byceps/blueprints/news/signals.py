"""
byceps.blueprints.news.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


news_signals = Namespace()


item_published = news_signals.signal('item-published')
