"""
byceps.blueprints.site.authentication.login.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import structlog

from .....services.authentication import authn_service
from .....services.authentication.errors import AuthenticationFailed
from .....services.authentication.session import authn_session_service
from .....services.authentication.session.authn_session_service import (
    UserLoggedIn,
)
from .....services.consent import consent_service, consent_subject_service
from .....services.site.models import SiteID
from .....services.user.models.user import User
from .....services.verification_token import verification_token_service
from .....typing import BrandID, UserID
from .....util import user_session
from .....util.result import Err, Ok, Result


log = structlog.get_logger()


@dataclass(frozen=True)
class ConsentRequired:
    verification_token: str


def log_in_user(
    username: str,
    password: str,
    permanent: bool,
    brand_id: BrandID,
    *,
    ip_address: Optional[str] = None,
    site_id: Optional[SiteID] = None,
) -> Result[tuple[User, UserLoggedIn], AuthenticationFailed | ConsentRequired]:
    authn_result = authn_service.authenticate(username, password)
    if authn_result.is_err():
        log.info(
            'User authentication failed',
            scope='site',
            username=username,
            error=str(authn_result.unwrap_err()),
        )
        return Err(authn_result.unwrap_err())

    user = authn_result.unwrap()

    # Authentication succeeded.

    if _is_consent_required(user.id, brand_id):
        verification_token = verification_token_service.create_for_consent(
            user.id
        )
        return Err(ConsentRequired(verification_token.token))

    auth_token, logged_in_event = authn_session_service.log_in_user(
        user.id, ip_address=ip_address, site_id=site_id
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    log.info(
        'User logged in',
        scope='site',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )

    return Ok((user, logged_in_event))


def _is_consent_required(user_id: UserID, brand_id: BrandID) -> bool:
    required_subject_ids = (
        consent_subject_service.get_subject_ids_required_for_brand(brand_id)
    )

    return not consent_service.has_user_consented_to_all_subjects(
        user_id, required_subject_ids
    )


def log_out_user(user: User) -> None:
    user_session.end()

    log.info(
        'User logged out',
        scope='site',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )
