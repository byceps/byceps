"""
byceps.blueprints.tourney.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


tourney_signals = Namespace()


tourney_started  = tourney_signals.signal('tourney-started')
tourney_paused   = tourney_signals.signal('tourney-paused')
tourney_canceled = tourney_signals.signal('tourney-canceled')
tourney_finished = tourney_signals.signal('tourney-finished')

match_ready            = tourney_signals.signal('tourney-match-ready')
match_reset            = tourney_signals.signal('tourney-match-reset')
match_score_submitted  = tourney_signals.signal('tourney-match-score-submitted')
match_score_confirmed  = tourney_signals.signal('tourney-match-score-confirmed')
match_score_randomized = tourney_signals.signal('tourney-match-score-randomized')
match_comment_created  = tourney_signals.signal('tourney-match-comment-created')

team_ready        = tourney_signals.signal('tourney-team-ready')
team_eliminated   = tourney_signals.signal('tourney-team-eliminated')
team_warned       = tourney_signals.signal('tourney-team-warned')
team_disqualified = tourney_signals.signal('tourney-team-disqualified')
