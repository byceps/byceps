# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import abort, redirect

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated

from ..verification_token import service as verification_token_service

from .models import Version
from . import service


blueprint = create_blueprint('terms', __name__)


@blueprint.route('/')
@templated
def view_current():
    """Show the current version of this brand's terms and conditions."""
    version = service.get_current_version()
    return {'version': version}


@blueprint.route('/<uuid:version_id>/accept/<uuid:token>')
@templated
def accept(version_id, token):
    """Accept that version of the terms."""
    version = Version.query.get_or_404(version_id)

    verification_token = verification_token_service.find_for_terms_consent_by_token(token)
    if verification_token is None:
        flash_error('Unbekannter Bestätigungscode.')
        abort(404)

    user = verification_token.user
    db.session.delete(verification_token)

    consent = service.build_consent_on_separate_action(user, version)
    db.session.add(consent)

    db.session.commit()

    flash_success('Du hast die AGB akzeptiert.')
    return redirect('/')
