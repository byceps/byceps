"""
byceps.services.whereabouts.blueprints.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pydantic import BaseModel


class RegisterClientRequestModel(BaseModel):
    button_count: int
    audio_output: bool


class SetStatusRequestModel(BaseModel):
    user_id: str
    party_id: str
    whereabouts_name: str
