"""
byceps.services.snippet.blueprints.api.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import jsonify

from byceps.services.snippet import snippet_service
from byceps.services.snippet.blueprints.site.templating import (
    get_rendered_snippet_body,
)
from byceps.services.snippet.models import SnippetScope
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import api_token_required, create_empty_json_response


blueprint = create_blueprint('snippet_api', __name__)


@blueprint.get(
    '/by_name/<scope_type>/<scope_name>/<snippet_name>/<language_code>'
)
@api_token_required
def get_snippet_by_name(scope_type, scope_name, snippet_name, language_code):
    """Return the current version of the snippet with that name in that
    scope.
    """
    scope = SnippetScope(scope_type, scope_name)
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
