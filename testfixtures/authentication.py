# -*- coding: utf-8 -*-

"""
testfixtures.authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import uuid4

from byceps.blueprints.authentication.models import SessionToken


def create_session_token(user_id, *, token=None, created_at=None):
    if token is None:
        token = uuid4()

    if created_at is None:
        created_at = datetime.utcnow()

    return SessionToken(token, user_id, created_at)
