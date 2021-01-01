"""
byceps.blueprints.site.consent.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from flask import abort, g, request

from ....services.consent import consent_service, subject_service
from ....services.verification_token import (
    service as verification_token_service,
)
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

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

    subject_ids_from_form = set(map(UUID, form.subject_ids.data.split(',')))

    try:
        subject_service.get_subjects(subject_ids_from_form)
    except subject_service.UnknownSubjectId:
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
    required_subject_ids = subject_service.get_subject_ids_required_for_brand(
        g.brand_id
    )

    unconsented_subject_ids = consent_service.get_unconsented_subject_ids(
        user_id, required_subject_ids
    )

    return subject_service.get_subjects(unconsented_subject_ids)


def _get_verification_token_or_404(token_value):
    verification_token = verification_token_service.find_for_terms_consent_by_token(
        token_value
    )

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    return verification_token
