"""
byceps.signals.news
~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


news_signals = Namespace()


item_published = news_signals.signal('item-published')
