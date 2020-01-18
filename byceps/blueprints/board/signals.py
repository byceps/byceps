"""
byceps.blueprints.board.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


board_signals = Namespace()


# postings

posting_created = board_signals.signal('posting-created')
posting_updated = board_signals.signal('posting-updated')

posting_hidden = board_signals.signal('posting-hidden')
posting_unhidden = board_signals.signal('posting-unhidden')


# topics

topic_created = board_signals.signal('topic-created')
topic_updated = board_signals.signal('topic-updated')

topic_hidden = board_signals.signal('topic-hidden')
topic_unhidden = board_signals.signal('topic-unhidden')

topic_locked = board_signals.signal('topic-locked')
topic_unlocked = board_signals.signal('topic-unlocked')

topic_pinned = board_signals.signal('topic-pinned')
topic_unpinned = board_signals.signal('topic-unpinned')

topic_moved = board_signals.signal('topic-moved')
