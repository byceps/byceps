"""
byceps.services.language.language_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import select

from byceps.database import db

from .dbmodels import DbLanguage
from .models import Language


def create_language(language: Language) -> None:
    """Create a language."""
    db_language = DbLanguage(language.code)
    db.session.add(db_language)
    db.session.commit()


def get_languages() -> Sequence[DbLanguage]:
    """Return all languages."""
    return db.session.scalars(select(DbLanguage)).all()
