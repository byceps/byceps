"""
byceps.blueprints.consent.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import UUID

from flask import abort, request

from ...services.consent import consent_service, subject_service
from ...services.verification_token import service as verification_token_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to

from ..authentication.views import _get_required_consent_subject_ids

from .forms import create_consent_form, get_subject_field_name


blueprint = create_blueprint('consent', __name__)


@blueprint.route('/consent/<token>')
@templated
def consent_form(token, *, erroneous_form=None):
    """Show form requiring consent to required subjects to which the
    user did not consent yet.
    """
    verification_token = _get_verification_token_or_404(token)

    user_id = verification_token.user_id

    unconsented_subjects = _get_unconsented_subjects_for_user(user_id)

    ConsentForm = create_consent_form(unconsented_subjects)
    form = erroneous_form if erroneous_form else ConsentForm()

    subjects_and_fields = _get_subjects_and_fields(unconsented_subjects, form)

    return {
        'token': token,
        'form': form,
        'subjects_and_fields': subjects_and_fields,
    }


def _get_subjects_and_fields(subjects, form):
    field_names = [get_subject_field_name(subject) for subject in subjects]
    fields = [getattr(form, field_name) for field_name in field_names]
    return list(zip(subjects, fields))


@blueprint.route('/consent/<token>', methods=['POST'])
def consent(token):
    """Consent to the specified subjects."""
    verification_token = _get_verification_token_or_404(token)

    user_id = verification_token.user_id

    unconsented_subjects = _get_unconsented_subjects_for_user(user_id)

    ConsentForm = create_consent_form(unconsented_subjects)
    form = ConsentForm(request.form)
    if not form.validate():
        return consent_form(token, erroneous_form=form)

    subject_ids_from_form = [
        UUID(id_str) for id_str in form.subject_ids.data.split(',')
    ]

    for subject_id in subject_ids_from_form:
        subject = subject_service.find_subject(subject_id)
        if subject is None:
            flash_error('Unbekanntes Zustimmungsthema')
            return consent_form(token, erroneous_form=form)

    expressed_at = datetime.utcnow()
    consent_service.consent_to_subjects(
        subject_ids_from_form, expressed_at, verification_token
    )

    flash_success(
        'Vielen Dank für deine Zustimmung. Bitte melde dich erneut an.'
    )
    return redirect_to('authentication.login_form')


def _get_unconsented_subjects_for_user(user_id):
    required_consent_subject_ids = _get_required_consent_subject_ids()

    unconsented_subject_ids = _get_unconsented_subject_ids(
        user_id, required_consent_subject_ids
    )

    return _get_subjects(unconsented_subject_ids)


def _get_unconsented_subject_ids(user_id, required_subject_ids):
    subject_ids = []

    for subject_id in required_subject_ids:
        if not consent_service.has_user_consented_to_subject(
            user_id, subject_id
        ):
            subject_ids.append(subject_id)

    return subject_ids


def _get_subjects(subject_ids):
    return [
        subject_service.find_subject(subject_id) for subject_id in subject_ids
    ]


def _get_verification_token_or_404(token_value):
    verification_token = verification_token_service.find_for_terms_consent_by_token(
        token_value
    )

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    return verification_token
