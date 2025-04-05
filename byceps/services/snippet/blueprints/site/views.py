"""
byceps.services.snippet.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.framework.blueprint import create_blueprint

from .templating import render_snippet_as_partial_from_template


blueprint = create_blueprint('snippet', __name__)

blueprint.add_app_template_global(
    render_snippet_as_partial_from_template, 'render_snippet'
)
