"""
byceps.blueprints.admin.language.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from babel import Locale

from ....services.language import language_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required


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
