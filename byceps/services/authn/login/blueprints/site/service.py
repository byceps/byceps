"""
byceps.services.authn.login.blueprints.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

import structlog

from byceps.services.authn import authn_service
from byceps.services.authn.errors import AuthenticationFailedError
from byceps.services.authn.events import UserLoggedInToSiteEvent
from byceps.services.authn.session import authn_session_service
from byceps.services.brand.models import BrandID
from byceps.services.consent import consent_service, consent_subject_service
from byceps.services.site.models import Site
from byceps.services.user.models.user import Password, User, UserID
from byceps.services.verification_token import verification_token_service
from byceps.util import user_session
from byceps.util.result import Err, Ok, Result


log = structlog.get_logger()


@dataclass(frozen=True)
class ConsentRequiredError:
    verification_token: str


def log_in_user(
    username: str,
    password: Password,
    permanent: bool,
    ip_address: str | None,
    brand_id: BrandID,
    site: Site,
) -> Result[
    tuple[User, UserLoggedInToSiteEvent],
    AuthenticationFailedError | ConsentRequiredError,
]:
    authn_result = authn_service.authenticate(username, password)
    if authn_result.is_err():
        log.info(
            'User authentication failed',
            scope='site',
            site_id=site.id,
            username=username,
            error=str(authn_result.unwrap_err()),
        )
        return Err(authn_result.unwrap_err())

    user = authn_result.unwrap()

    # Authentication succeeded.

    if _is_consent_required(user.id, brand_id):
        consent_token = verification_token_service.create_for_consent(user)
        return Err(ConsentRequiredError(consent_token.token))

    auth_token, logged_in_event = authn_session_service.log_in_user_to_site(
        user, ip_address, site=site
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    log.info(
        'User logged in to site',
        site_id=site.id,
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


def log_out_user(user: User, site: Site) -> None:
    user_session.end()

    log.info(
        'User logged out of site',
        site_id=site.id,
        user_id=str(user.id),
        screen_name=user.screen_name,
    )
