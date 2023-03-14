"""
byceps.blueprints.api.v1.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import jsonify

from .....services.snippet.models import Scope
from .....services.snippet import snippet_service
from .....util.framework.blueprint import create_blueprint
from .....util.views import create_empty_json_response

from ....site.snippet.templating import get_rendered_snippet_body

from ...decorators import api_token_required


blueprint = create_blueprint('snippet_api', __name__)


@blueprint.get(
    '/by_name/<scope_type>/<scope_name>/<snippet_name>/<language_code>'
)
@api_token_required
def get_snippet_by_name(scope_type, scope_name, snippet_name, language_code):
    """Return the current version of the snippet with that name in that
    scope.
    """
    scope = Scope(scope_type, scope_name)
    version = snippet_service.find_current_version_of_snippet_with_name(
        scope, snippet_name, language_code
    )
    if version is None:
        return create_empty_json_response(404)

    content = {'body': get_rendered_snippet_body(version)}

    return jsonify(
        {
            'version': version.id,
            'content': content,
        }
    )
