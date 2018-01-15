"""
byceps.blueprints.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, jsonify

from ...services.snippet import service as snippet_service
from ...util.framework.blueprint import create_blueprint
from ...util.views import create_empty_json_response

from .templating import get_snippet_context, render_snippet_as_page, \
    render_snippet_as_partial


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(render_snippet_as_partial, 'render_snippet')


def view_latest_by_name(name):
    """Show the latest version of the snippet with the given name."""
    # TODO: Fetch snippet via mountpoint
    # endpoint suffix != snippet name
    version = _find_current_snippet_version(name)
    if version is None:
        abort(404)

    return render_snippet_as_page(version)


@blueprint.route('/by_name/<name>.json')
def view_as_json(name):
    """Return the current version of the snippet with that name as JSON."""
    version = _find_current_snippet_version(name)
    if version is None:
        return create_empty_json_response(404)

    context = get_snippet_context(version)

    content = {
        'body': context['body'],
    }

    if version.snippet.is_document:
        content.update({
            'title': context['title'],
            'head': context['head'],
        })

    return jsonify({
        'type': version.snippet.type_.name,
        'version': version.id,
        'content': content,
    })


def _find_current_snippet_version(name):
    """Return the current version of the snippet with that name, or
    `None` if it does not exist.
    """
    return snippet_service.find_current_version_of_snippet_with_name(
        g.party_id, name)
