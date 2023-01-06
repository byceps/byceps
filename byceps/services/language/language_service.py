"""
byceps.services.language.language_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from ...database import db

from .dbmodels import DbLanguage
from .transfer.models import Language


def create_language(code: str) -> Language:
    """Create a language."""
    db_language = DbLanguage(code)
    db.session.add(db_language)
    db.session.commit()

    return _db_entity_to_language(db_language)


def get_languages() -> list[Language]:
    """Return all languages."""
    db_languages = db.session.scalars(select(DbLanguage)).all()

    return [_db_entity_to_language(db_language) for db_language in db_languages]


def _db_entity_to_language(db_language: DbLanguage) -> Language:
    return Language(code=db_language.code)
