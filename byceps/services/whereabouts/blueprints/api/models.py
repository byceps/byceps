"""
byceps.services.whereabouts.blueprints.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pydantic import BaseModel


class RegisterClientRequest(BaseModel):
    button_count: int
    audio_output: bool


class SetStatusRequest(BaseModel):
    user_id: UUID
    party_id: str
    whereabouts_name: str
