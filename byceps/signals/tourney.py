"""
byceps.signals.tourney
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
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

participant_ready        = tourney_signals.signal('tourney-participant-ready')
participant_eliminated   = tourney_signals.signal('tourney-participant-eliminated')
participant_warned       = tourney_signals.signal('tourney-participant-warned')
participant_disqualified = tourney_signals.signal('tourney-participant-disqualified')
