"""
byceps.blueprints.admin.consent.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from ....services.brand import brand_service
from ....services.consent import (
    brand_requirements_service,
    consent_subject_service,
)
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, redirect_to

from .forms import RequirementCreateForm, SubjectCreateForm


blueprint = create_blueprint('consent_admin', __name__)


# -------------------------------------------------------------------- #
# subjects


@blueprint.get('/subjects')
@permission_required('consent.administrate')
@templated
def subject_index():
    """List consent subjects."""
    subjects_with_consent_counts = (
        consent_subject_service.get_subjects_with_consent_counts()
    )

    subjects_with_consent_counts = list(subjects_with_consent_counts.items())

    return {
        'subjects_with_consent_counts': subjects_with_consent_counts,
    }


@blueprint.get('/subjects/create')
@permission_required('consent.administrate')
@templated
def subject_create_form(erroneous_form=None):
    """Show form to create a consent subject."""
    form = erroneous_form if erroneous_form else SubjectCreateForm()

    return {
        'form': form,
    }


@blueprint.post('/subjects')
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

    subject = consent_subject_service.create_subject(
        subject_name, subject_title, checkbox_label, checkbox_link_target
    )

    flash_success(
        gettext(
            'Consent subject "%(title)s" has been created.', title=subject.title
        )
    )

    return redirect_to('.subject_index')


# -------------------------------------------------------------------- #
# brand requirements


@blueprint.get('/requirements/for_brand/<brand_id>')
@permission_required('consent.administrate')
@templated
def requirement_index(brand_id):
    """List consent requirements for the brand."""
    brand = _get_brand_or_404(brand_id)

    subject_ids = consent_subject_service.get_subject_ids_required_for_brand(
        brand.id
    )

    subjects_to_consent_counts = (
        consent_subject_service.get_subjects_with_consent_counts(
            limit_to_subject_ids=subject_ids
        )
    )

    subjects_with_consent_counts = sorted(
        subjects_to_consent_counts.items(), key=lambda x: x[0].title
    )

    return {
        'brand': brand,
        'subjects_with_consent_counts': subjects_with_consent_counts,
    }


@blueprint.get('/requirements/for_brand/<brand_id>/create')
@permission_required('consent.administrate')
@templated
def requirement_create_form(brand_id, erroneous_form=None):
    """Show form to create a consent requirement for a brand."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else RequirementCreateForm()
    form.set_subject_id_choices(brand.id)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/requirements/for_brand/<brand_id>')
@permission_required('consent.administrate')
def requirement_create(brand_id):
    """Create a consent requirement for a brand."""
    brand = _get_brand_or_404(brand_id)

    form = RequirementCreateForm(request.form)
    form.set_subject_id_choices(brand.id)

    if not form.validate():
        return requirement_create_form(brand.id, form)

    subject_id = form.subject_id.data

    brand_requirements_service.create_brand_requirement(brand.id, subject_id)

    flash_success(gettext('The requirement has been created.'))

    return redirect_to('.requirement_index', brand_id=brand.id)


# -------------------------------------------------------------------- #


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand
