"""
byceps.services.language.language_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db

from .dbmodels import DbLanguage
from .models import Language


def create_language(code: str) -> Language:
    """Create a language."""
    language = Language(code=code)

    db_language = DbLanguage(language.code)
    db.session.add(db_language)
    db.session.commit()

    return language


def get_languages() -> list[Language]:
    """Return all languages."""
    db_languages = db.session.scalars(select(DbLanguage)).all()

    return [_db_entity_to_language(db_language) for db_language in db_languages]


def _db_entity_to_language(db_language: DbLanguage) -> Language:
    return Language(code=db_language.code)
