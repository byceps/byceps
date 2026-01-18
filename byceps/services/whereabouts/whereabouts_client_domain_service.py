"""
byceps.services.whereabouts.whereabouts_client_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
import secrets

from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .events import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsClientDeletedEvent,
    WhereaboutsClientSignedOffEvent,
    WhereaboutsClientSignedOnEvent,
)
from .models import (
    WhereaboutsClient,
    WhereaboutsClientAuthorityStatus,
    WhereaboutsClientCandidate,
    WhereaboutsClientConfig,
    WhereaboutsClientConfigID,
    WhereaboutsClientID,
)


def register_client(
    button_count: int, audio_output: bool
) -> tuple[WhereaboutsClientCandidate, WhereaboutsClientRegisteredEvent]:
    """Register a client."""
    client_id = WhereaboutsClientID(generate_uuid7())
    registered_at = datetime.utcnow()
    token = 'VerbleiberClientToken_' + secrets.token_urlsafe(24)

    candidate = WhereaboutsClientCandidate(
        id=client_id,
        registered_at=registered_at,
        button_count=button_count,
        audio_output=audio_output,
        token=token,
    )

    event = WhereaboutsClientRegisteredEvent(
        occurred_at=registered_at,
        initiator=None,
        client_id=client_id,
    )

    return candidate, event


def approve_client(
    candidate: WhereaboutsClientCandidate, initiator: User
) -> tuple[WhereaboutsClient, WhereaboutsClientApprovedEvent]:
    """Approve a client."""
    approved_at = datetime.utcnow()

    client = WhereaboutsClient(
        id=candidate.id,
        registered_at=candidate.registered_at,
        button_count=candidate.button_count,
        audio_output=candidate.audio_output,
        authority_status=WhereaboutsClientAuthorityStatus.approved,
        token=candidate.token,
        name=None,
        location=None,
        description=None,
        config_id=None,
        signed_on=False,
        latest_activity_at=candidate.registered_at,
    )

    event = WhereaboutsClientApprovedEvent(
        occurred_at=approved_at,
        initiator=initiator,
        client_id=client.id,
    )

    return client, event


def update_client(
    client: WhereaboutsClient,
    name: str | None,
    location: str | None,
    description: str | None,
) -> WhereaboutsClient:
    """Update a client."""
    return dataclasses.replace(
        client, name=name, location=location, description=description
    )


def delete_client(
    client: WhereaboutsClient, initiator: User
) -> tuple[WhereaboutsClient, WhereaboutsClientDeletedEvent]:
    """Delete a client."""
    deleted_at = datetime.utcnow()

    deleted_client = dataclasses.replace(
        client,
        authority_status=WhereaboutsClientAuthorityStatus.deleted,
        token=None,
    )

    event = WhereaboutsClientDeletedEvent(
        occurred_at=deleted_at,
        initiator=initiator,
        client_id=client.id,
    )

    return deleted_client, event


def sign_on_client(client: WhereaboutsClient) -> WhereaboutsClientSignedOnEvent:
    """Sign on a client."""
    signed_on_at = datetime.utcnow()

    event = WhereaboutsClientSignedOnEvent(
        occurred_at=signed_on_at,
        initiator=None,
        client_id=client.id,
    )

    return event


def sign_off_client(
    client: WhereaboutsClient,
) -> WhereaboutsClientSignedOffEvent:
    """Sign off a client."""
    signed_on_at = datetime.utcnow()

    event = WhereaboutsClientSignedOffEvent(
        occurred_at=signed_on_at,
        initiator=None,
        client_id=client.id,
    )

    return event


def create_client_config(
    title: str,
    description: str | None,
    content: str,
) -> WhereaboutsClientConfig:
    """Create a client configuration."""
    config_id = WhereaboutsClientConfigID(generate_uuid7())

    return WhereaboutsClientConfig(
        id=config_id,
        title=title,
        description=description,
        content=content,
    )
