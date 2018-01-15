"""
byceps.blueprints.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ...services.terms import service as terms_service
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
    version = terms_service.get_current_version(g.brand_id)

    return {
        'version': version,
    }


@blueprint.route('/<uuid:version_id>/consent/<uuid:token>')
@templated
def consent_form(version_id, token, *, erroneous_form=None):
    """Show that version of the terms, and a form to consent to it."""
    version = _get_version_or_404(version_id)

    verification_token = verification_token_service \
        .find_for_terms_consent_by_token(token)

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    form = erroneous_form if erroneous_form else ConsentForm()

    return {
        'version': version,
        'token': token,
        'form': form,
    }


@blueprint.route('/<uuid:version_id>/consent/<uuid:token>', methods=['POST'])
def consent(version_id, token):
    """Consent to that version of the terms."""
    version = _get_version_or_404(version_id)

    verification_token = verification_token_service \
        .find_for_terms_consent_by_token(token)

    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    form = ConsentForm(request.form)
    if not form.validate():
        return consent_form(version_id, token, erroneous_form=form)

    terms_service.consent_to_version_on_separate_action(version.id,
                                                        verification_token)

    flash_success('Du hast die AGB akzeptiert.')
    return redirect_to('authentication.login_form')


def _get_version_or_404(version_id):
    version = terms_service.find_version(version_id)

    if version is None:
        abort(404)

    return version
