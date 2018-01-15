"""
byceps.blueprints.tourney.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


tourney_signals = Namespace()


match_comment_created = tourney_signals.signal('match-comment-created')
