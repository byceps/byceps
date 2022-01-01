"""
byceps.blueprints.admin.consent.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import request
from flask_babel import gettext

from ....services.consent import subject_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to

from .forms import SubjectCreateForm


blueprint = create_blueprint('consent_admin', __name__)


@blueprint.get('/')
@permission_required('consent.administrate')
@templated
def index():
    """List consent subjects."""
    subjects_with_consent_counts = (
        subject_service.get_subjects_with_consent_counts()
    )

    subjects_with_consent_counts = list(subjects_with_consent_counts.items())

    return {
        'subjects_with_consent_counts': subjects_with_consent_counts,
    }


@blueprint.get('/consents/create')
@permission_required('consent.administrate')
@templated
def subject_create_form(erroneous_form=None):
    """Show form to create a consent subject."""
    form = erroneous_form if erroneous_form else SubjectCreateForm()

    return {
        'form': form,
    }


@blueprint.post('/consents')
@permission_required('consent.administrate')
def subject_create():
    """Create a consent subject."""
    form = SubjectCreateForm(request.form)
    if not form.validate():
        return subject_create_form(form)

    subject_name = form.subject_name.data.strip()
    subject_title = form.subject_title.data.strip()
    checkbox_label = form.checkbox_label.data.strip()
    checkbox_link_target = form.checkbox_link_target.data.strip()

    subject = subject_service.create_subject(
        subject_name, subject_title, checkbox_label, checkbox_link_target
    )

    flash_success(
        gettext(
            'Consent subject "%(title)s" has been created.', title=subject.title
        )
    )

    return redirect_to('.index')
