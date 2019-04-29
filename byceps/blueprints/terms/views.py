"""
byceps.blueprints.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import abort, g, request

from ...services.consent import consent_service
from ...services.terms import version_service as terms_version_service
from ...services.verification_token import service as verification_token_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to

from .forms import ConsentForm


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
    terms_version = terms_version_service.find_current_version(g.brand_id)

    verification_token = verification_token_service \
        .find_for_terms_consent_by_token(token)

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    form = erroneous_form if erroneous_form \
        else ConsentForm(terms_version_id=terms_version.id)

    return {
        'terms_version': terms_version,
        'token': token,
        'form': form,
    }


@blueprint.route('/consent/<uuid:token>', methods=['POST'])
def consent(token):
    """Consent to that version of the terms."""
    verification_token = verification_token_service \
        .find_for_terms_consent_by_token(token)

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    form = ConsentForm(request.form)
    if not form.validate():
        return consent_form(token, erroneous_form=form)

    terms_version_id = form.terms_version_id.data
    terms_version = terms_version_service.find_version(terms_version_id)
    if terms_version is None:
        flash_error('Unbekannte AGB-Version.')
        abort(404)

    expressed_at = datetime.utcnow()
    consent_service.consent_to_subject(
        terms_version.consent_subject_id, expressed_at, verification_token)

    flash_success('Du hast die AGB akzeptiert.')
    return redirect_to('authentication.login_form')
