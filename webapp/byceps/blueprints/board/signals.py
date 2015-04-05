# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from blinker import Namespace


board_signals = Namespace()


posting_created = board_signals.signal('posting-created')
posting_hidden = board_signals.signal('posting-hidden')
topic_created = board_signals.signal('topic-created')
topic_hidden = board_signals.signal('topic-hidden')
