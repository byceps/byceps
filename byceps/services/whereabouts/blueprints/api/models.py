"""
byceps.services.whereabouts.blueprints.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class RegisterClientRequest:
    button_count: int
    audio_output: bool


@dataclass(frozen=True, kw_only=True)
class SetStatusRequest:
    user_id: UUID
    party_id: str
    whereabouts_name: str
