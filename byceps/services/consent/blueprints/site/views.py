"""
byceps.services.consent.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.consent import consent_service, consent_subject_service
from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import ConsentToken
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to

from .forms import create_consent_form, get_subject_field_name


blueprint = create_blueprint('consent', __name__)


@blueprint.get('/consent/<token>')
@templated
def consent_form(token, *, erroneous_form=None):
    """Show form requiring consent to required subjects to which the
    user did not consent yet.
    """
    consent_token = _get_consent_token_or_404(token)

    user = consent_token.user

    unconsented_subjects = _get_unconsented_subjects_for_user(user.id)

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
    return list(zip(subjects, fields, strict=True))


@blueprint.post('/consent/<token>')
def consent(token):
    """Consent to the specified subjects."""
    consent_token = _get_consent_token_or_404(token)

    user = consent_token.user

    unconsented_subjects = _get_unconsented_subjects_for_user(user.id)

    ConsentForm = create_consent_form(unconsented_subjects)
    form = ConsentForm(request.form)
    if not form.validate():
        return consent_form(token, erroneous_form=form)

    subject_ids_from_form = set(map(UUID, form.subject_ids.data.split(',')))

    try:
        consent_subject_service.get_subjects(subject_ids_from_form)
    except consent_subject_service.UnknownSubjectIdError:
        flash_error(gettext('Unknown consent subject'))
        return consent_form(token, erroneous_form=form)

    expressed_at = datetime.utcnow()
    consent_service.consent_to_subjects(
        user.id, subject_ids_from_form, expressed_at
    )
    verification_token_service.delete_token(consent_token.token)

    flash_success(gettext('Thank you for your consent. Please log in again.'))
    return redirect_to('authn_login.log_in_form')


def _get_unconsented_subjects_for_user(user_id):
    required_subject_ids = (
        consent_subject_service.get_subject_ids_required_for_brand(
            g.site.brand_id
        )
    )

    unconsented_subject_ids = consent_service.get_unconsented_subject_ids(
        user_id, required_subject_ids
    )

    return consent_subject_service.get_subjects(unconsented_subject_ids)


def _get_consent_token_or_404(token_value: str) -> ConsentToken:
    consent_token = verification_token_service.find_for_consent_by_token(
        token_value
    )

    if consent_token is None:
        flash_error(gettext('Invalid verification token'))
        abort(404)

    return consent_token
