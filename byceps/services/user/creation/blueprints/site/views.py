"""
byceps.services.user.creation.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import abort, g, request, current_app
from flask_babel import gettext
from secret_type import secret

from byceps.services.brand import brand_service
from byceps.services.consent import consent_service, consent_subject_service
from byceps.services.consent.models import ConsentSubject
from byceps.services.newsletter import newsletter_command_service
from byceps.services.newsletter.models import List as NewsletterList
from byceps.services.site import site_setting_service
from byceps.services.user import signals as user_signals, user_creation_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to

from byceps.util.turnstile import get_public_options, verify_token, best_remote_ip

from .forms import assemble_user_create_form


blueprint = create_blueprint('user_creation', __name__)


@blueprint.get('/create')
@templated
def create_form(erroneous_form=None):
    """Show a form to create a user."""
    _abort_if_user_account_creation_disabled()

    required_consent_subjects = _get_required_consent_subjects()
    newsletter_list = _find_newsletter_list_for_brand()

    real_name_required = _is_real_name_required()
    newsletter_offered = newsletter_list is not None

    if erroneous_form:
        form = erroneous_form
    else:
        UserCreateForm = assemble_user_create_form(
            real_name_required=real_name_required,
            required_consent_subjects=required_consent_subjects,
            newsletter_offered=newsletter_offered,
        )
        form = UserCreateForm()

    return {
        'form': form,
        'required_consent_subjects': required_consent_subjects,
        'turnstile': get_public_options(),
    }


@blueprint.post('/')
def create():
    """Create a user."""
    _abort_if_user_account_creation_disabled()

    required_consent_subjects = _get_required_consent_subjects()
    newsletter_list = _find_newsletter_list_for_brand()

    real_name_required = _is_real_name_required()
    newsletter_offered = newsletter_list is not None

    UserCreateForm = assemble_user_create_form(
        real_name_required=real_name_required,
        required_consent_subjects=required_consent_subjects,
        newsletter_offered=newsletter_offered,
    )
    form = UserCreateForm(request.form)

    if not form.validate():
        return create_form(form)

    if current_app.config.get('TURNSTILE_ENABLED'):
        token = (request.form.get('cf-turnstile-response') or '').strip()
        if not token:
            flash_error(gettext('Captcha token missing.'))
            return create_form(form)
        ok = verify_token(
            token,
            remoteip=best_remote_ip(request),
            timeout=3.0,
            expected_action='user_create',
        )
        if not ok:
            flash_error(gettext('Captcha verification failed.'))
            return create_form(form)

    screen_name = form.screen_name.data.strip()
    email_address = form.email_address.data.strip()
    password = secret(form.password.data)

    now_utc = datetime.utcnow()

    if real_name_required:
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
    else:
        first_name = None
        last_name = None

    creation_result = user_creation_service.create_user(
        screen_name,
        email_address,
        password,
        first_name=first_name,
        last_name=last_name,
        creation_method='site app',
        site=g.site,
        ip_address=request.remote_addr,
    )
    if creation_result.is_err():
        flash_error(
            gettext(
                'User "%(screen_name)s" could not be created.',
                screen_name=screen_name,
            )
        )
        return create_form(form)

    user, event = creation_result.unwrap()

    user_creation_service.request_email_address_confirmation(
        user, email_address, g.site.id
    ).unwrap()

    subject_ids = {subject.id for subject in required_consent_subjects}
    consent_service.consent_to_subjects(user.id, subject_ids, now_utc)

    flash_success(
        gettext(
            'User "%(screen_name)s" has been created. Before you can log in, '
            'please visit the link emailed to you to verify your email address.',
            screen_name=user.screen_name,
        )
    )

    user_signals.account_created.send(None, event=event)

    if newsletter_offered:
        subscribe_to_newsletter = form.subscribe_to_newsletter.data
        if subscribe_to_newsletter:
            initiator = user
            newsletter_command_service.subscribe_user_to_list(
                user, newsletter_list, now_utc, initiator
            ).unwrap()

    return redirect_to('authn_login.log_in_form')


def _abort_if_user_account_creation_disabled():
    if not g.site.user_account_creation_enabled:
        flash_error(gettext('User account creation is disabled.'))
        abort(403)


def _is_real_name_required() -> bool:
    """Return `True` if real name is required.

    By default, real name is required. It can be disabled by configuring
    the string `false` for the site setting `real_name_required`.
    """
    value = _find_site_setting_value('real_name_required')

    return value != 'false'


def _get_required_consent_subjects() -> set[ConsentSubject]:
    """Return the consent subjects required for this brand."""
    return consent_subject_service.get_subjects_required_for_brand(
        g.site.brand_id
    )


def _find_newsletter_list_for_brand() -> NewsletterList | None:
    """Return the newsletter list configured for this brand, or `None`
    if none is configured.
    """
    return brand_service.find_newsletter_list_for_brand(g.site.brand_id)


def _find_site_setting_value(setting_name: str) -> str | None:
    """Return the value configured for this site and the given setting
    name, or `None` if not configured.
    """
    return site_setting_service.find_setting_value(g.site.id, setting_name)
