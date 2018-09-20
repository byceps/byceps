"""
byceps.blueprints.tourney.match.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


tourney_match_signals = Namespace()


match_comment_created = tourney_match_signals.signal('match-comment-created')
