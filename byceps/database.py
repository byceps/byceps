"""
byceps.database
~~~~~~~~~~~~~~~

Database utilities.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import uuid

from flask_sqlalchemy import BaseQuery, SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID


db = SQLAlchemy(session_options={'autoflush': False})


db.JSONB = JSONB


class Uuid(UUID):

    def __init__(self):
        super().__init__(as_uuid=True)


db.Uuid = Uuid


def generate_uuid():
    """Generate a random UUID (Universally Unique IDentifier)."""
    return uuid.uuid4()
