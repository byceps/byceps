"""
byceps.blueprints.user.creation.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from flask import abort, g, request

from ....config import get_user_registration_enabled
from ....services.brand import settings_service as brand_settings_service
from ....services.consent.transfer.models import Consent, SubjectID
from ....services.newsletter.transfer.models import \
    ListID as NewsletterListID, Subscription as NewsletterSubscription
from ....services.terms import document_service as terms_document_service
from ....services.terms import version_service as terms_version_service
from ....services.user import creation_service as user_creation_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from .. import signals

from .forms import UserCreateForm


blueprint = create_blueprint('user_creation', __name__)


@blueprint.route('/create')
@templated
def create_form(erroneous_form=None):
    """Show a form to create a user."""
    if not get_user_registration_enabled():
        flash_error('Das Erstellen von Benutzerkonten ist deaktiviert.')
        abort(403)

    terms_version = terms_version_service \
        .find_current_version_for_brand(g.brand_id)

    privacy_policy_consent_subject_id \
        = _find_privacy_policy_consent_subject_id()

    newsletter_list_id = _find_newsletter_list_for_brand()

    real_name_required = _is_real_name_required()
    terms_consent_required = (terms_version is not None)
    privacy_policy_consent_required \
        = (privacy_policy_consent_subject_id is not None)
    newsletter_offered = (newsletter_list_id is not None)

    if terms_consent_required:
        terms_version_id = terms_version.id
    else:
        terms_version_id = None

    form = erroneous_form if erroneous_form \
        else UserCreateForm(terms_version_id=terms_version_id)

    _adjust_create_form(form, real_name_required, terms_consent_required,
                        privacy_policy_consent_required, newsletter_offered)

    return {'form': form}


@blueprint.route('/', methods=['POST'])
def create():
    """Create a user."""
    if not get_user_registration_enabled():
        flash_error('Das Erstellen von Benutzerkonten ist deaktiviert.')
        abort(403)

    terms_document_id = terms_document_service \
        .find_document_id_for_brand(g.brand_id)

    privacy_policy_consent_subject_id \
        = _find_privacy_policy_consent_subject_id()

    newsletter_list_id = _find_newsletter_list_for_brand()

    real_name_required = _is_real_name_required()
    terms_consent_required = (terms_document_id is not None)
    privacy_policy_consent_required \
        = (privacy_policy_consent_subject_id is not None)
    newsletter_offered = (newsletter_list_id is not None)

    form = UserCreateForm(request.form)

    _adjust_create_form(form, real_name_required, terms_consent_required,
                        privacy_policy_consent_required, newsletter_offered)

    if not form.validate():
        return create_form(form)

    screen_name = form.screen_name.data.strip()
    email_address = form.email_address.data.strip().lower()
    password = form.password.data

    now_utc = datetime.utcnow()

    if user_service.is_screen_name_already_assigned(screen_name):
        flash_error(
            'Dieser Benutzername ist bereits einem Benutzerkonto zugeordnet.')
        return create_form(form)

    if user_service.is_email_address_already_assigned(email_address):
        flash_error(
            'Diese E-Mail-Adresse ist bereits einem Benutzerkonto zugeordnet.')
        return create_form(form)

    if real_name_required:
        first_names = form.first_names.data.strip()
        last_name = form.last_name.data.strip()
    else:
        first_names = None
        last_name = None

    terms_consent = None
    if terms_consent_required:
        terms_version_id = form.terms_version_id.data
        consent_to_terms = form.consent_to_terms.data

        terms_version = terms_version_service.find_version(terms_version_id)
        if terms_version.document_id != terms_document_id:
            abort(400, 'Die AGB-Version gehört nicht zu dieser Veranstaltung.')

        terms_consent = Consent(
            user_id=None,  # not available at this point
            subject_id=terms_version.consent_subject_id,
            expressed_at=now_utc)

    privacy_policy_consent = None
    if privacy_policy_consent_required:
        privacy_policy_consent = Consent(
            user_id=None,  # not available at this point
            subject_id=privacy_policy_consent_subject_id,
            expressed_at=now_utc)

    newsletter_subscription = None
    if newsletter_offered:
        subscribe_to_newsletter = form.subscribe_to_newsletter.data
        if subscribe_to_newsletter:
            newsletter_subscription = NewsletterSubscription(
                user_id=None,  # not available at this point
                list_id=newsletter_list_id,
                expressed_at=now_utc)

    try:
        user = user_creation_service.create_user(
            screen_name, email_address, password, first_names, last_name,
            g.site_id, terms_consent=terms_consent,
            privacy_policy_consent=privacy_policy_consent,
            newsletter_subscription=newsletter_subscription)
    except user_creation_service.UserCreationFailed:
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    screen_name)
        return create_form(form)

    flash_success(
        'Das Benutzerkonto für "{}" wurde angelegt. '
        'Bevor du dich damit anmelden kannst, muss zunächst der Link in '
        'der an die angegebene Adresse verschickten E-Mail besucht werden.',
        user.screen_name)
    signals.account_created.send(None, user_id=user.id)

    return redirect_to('authentication.login_form')


def _adjust_create_form(form, real_name_required, terms_consent_required,
                        privacy_policy_consent_required, newsletter_offered):
    if not real_name_required:
        del form.first_names
        del form.last_name

    if not terms_consent_required:
        del form.terms_version_id
        del form.consent_to_terms

    if not privacy_policy_consent_required:
        del form.consent_to_privacy_policy

    if not newsletter_offered:
        del form.subscribe_to_newsletter


def _is_real_name_required() -> bool:
    """Return `True` if real name is required.

    By default, real name is required. It can be disabled by configuring
    the string `false` for the brand setting `real_name_required`.
    """
    value = _find_brand_setting_value('real_name_required')

    return value != 'false'


def _find_privacy_policy_consent_subject_id() -> Optional[SubjectID]:
    """Return the privacy policy consent subject ID configured for this
    brand, or `None` if none is configured.
    """
    value = _find_brand_setting_value('privacy_policy_consent_subject_id')

    if not value:
        return None

    return SubjectID(value)


def _find_newsletter_list_for_brand() -> Optional[NewsletterListID]:
    """Return the newsletter list configured for this brand, or `None`
    if none is configured.
    """
    value = _find_brand_setting_value('newsletter_list_id')

    if not value:
        return None

    return NewsletterListID(value)


def _find_brand_setting_value(setting_name: str) -> Optional[str]:
    """Return the value configured for this brand and the given setting
    name, or `None` if not configured.
    """
    return brand_settings_service.find_setting_value(g.brand_id, setting_name)
