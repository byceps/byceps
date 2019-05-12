"""
byceps.blueprints.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import UUID

from flask import abort, g, request

from ...services.consent import consent_service, subject_service
from ...services.terms import version_service as terms_version_service
from ...services.verification_token import service as verification_token_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to

from .forms import create_consent_form, get_subject_field_name


blueprint = create_blueprint('terms', __name__)


@blueprint.route('/')
@templated
def view_current():
    """Show the current version of this brand's terms and conditions."""
    version = terms_version_service.get_current_version(g.brand_id)

    return {
        'version': version,
    }


@blueprint.route('/consent/<uuid:token>')
@templated
def consent_form(token, *, erroneous_form=None):
    """Show that version of the terms, and a form to consent to it."""
    verification_token = _get_verification_token_or_404(token)

    terms_version = terms_version_service.find_current_version(g.brand_id)
    subjects = [terms_version.consent_subject]

    ConsentForm = create_consent_form(subjects)
    form = erroneous_form if erroneous_form else ConsentForm()

    field_names = [get_subject_field_name(subject) for subject in subjects]
    fields = [getattr(form, field_name) for field_name in field_names]

    return {
        'token': token,
        'form': form,
        'fields': fields,
    }


@blueprint.route('/consent/<uuid:token>', methods=['POST'])
def consent(token):
    """Consent to that version of the terms."""
    verification_token = _get_verification_token_or_404(token)

    terms_version = terms_version_service.find_current_version(g.brand_id)
    subjects_for_form = [terms_version.consent_subject]

    ConsentForm = create_consent_form(subjects_for_form)
    form = ConsentForm(request.form)
    if not form.validate():
        return consent_form(token, erroneous_form=form)

    subject_ids_from_form = [UUID(id_str)
                             for id_str in form.subject_ids.data.split(',')]

    for subject_id in subject_ids_from_form:
        subject = subject_service.find_subject(subject_id)
        if subject is None:
            flash_error('Unbekanntes Zustimmungsthema')
            return consent_form(token, erroneous_form=form)

    expressed_at = datetime.utcnow()
    consent_service.consent_to_subjects(subject_ids_from_form, expressed_at,
                                        verification_token)

    flash_success('Vielen Dank für deine Zustimmung. Bitte melde dich erneut an.')
    return redirect_to('authentication.login_form')


def _get_verification_token_or_404(token_str):
    verification_token = verification_token_service \
        .find_for_terms_consent_by_token(token_str)

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    return verification_token
