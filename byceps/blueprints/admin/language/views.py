"""
byceps.blueprints.admin.language.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from babel import Locale
from flask import request
from flask_babel import gettext

from byceps.services.language import language_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to

from .forms import CreateForm


blueprint = create_blueprint('language_admin', __name__)


@blueprint.get('')
@permission_required('admin.maintain')
@templated
def index():
    """List languages."""
    languages = language_service.get_languages()

    languages_and_locales = [
        (language, Locale(language.code)) for language in languages
    ]

    return {
        'languages_and_locales': languages_and_locales,
    }


@blueprint.get('/create')
@permission_required('admin.maintain')
@templated
def create_form(erroneous_form=None):
    """Show form to add a language."""
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.post('/')
@permission_required('admin.maintain')
def create():
    """Add a language."""
    form = CreateForm(request.form)

    if not form.validate():
        return create_form(form)

    code = form.code.data.strip()

    language_service.create_language(code)

    flash_success(gettext('Language has been added.'))

    return redirect_to('.index')
