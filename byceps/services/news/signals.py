"""
byceps.services.news.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


news_signals = Namespace()


item_published = news_signals.signal('item-published')
