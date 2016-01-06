# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..verification_token import service as verification_token_service

from .forms import ConsentForm
from .models import Version
from . import service


blueprint = create_blueprint('terms', __name__)


@blueprint.route('/')
@templated
def view_current():
    """Show the current version of this brand's terms and conditions."""
    version = service.get_current_version(g.party.brand)
    return {'version': version}


@blueprint.route('/<uuid:version_id>/consent/<uuid:token>')
@templated
def consent_form(version_id, token, *, erroneous_form=None):
    """Show that version of the terms, and a form to consent to it."""
    version = Version.query.get_or_404(version_id)

    verification_token = verification_token_service.find_for_terms_consent_by_token(token)
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
    version = Version.query.get_or_404(version_id)

    verification_token = verification_token_service.find_for_terms_consent_by_token(token)
    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    form = ConsentForm(request.form)
    if not form.validate():
        return consent_form(version_id, token, erroneous_form=form)

    user = verification_token.user
    db.session.delete(verification_token)

    consent = service.build_consent_on_separate_action(user, version)
    db.session.add(consent)

    db.session.commit()

    flash_success('Du hast die AGB akzeptiert.')
    return redirect_to('authentication.login_form')
