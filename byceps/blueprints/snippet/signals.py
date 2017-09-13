"""
byceps.blueprints.snippet.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


snippet_signals = Namespace()


document_created = snippet_signals.signal('document-created')
document_updated = snippet_signals.signal('document-updated')

fragment_created = snippet_signals.signal('fragment-created')
fragment_updated = snippet_signals.signal('fragment-updated')
