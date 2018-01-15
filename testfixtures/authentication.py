"""
testfixtures.authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import uuid4

from byceps.services.authentication.session.models import SessionToken


def create_session_token(user_id, *, token=None, created_at=None):
    if token is None:
        token = uuid4()

    if created_at is None:
        created_at = datetime.utcnow()

    return SessionToken(token, user_id, created_at)
