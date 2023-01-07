"""
byceps.blueprints.admin.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional
from flask import abort, g, request, url_for
from flask_babel import format_datetime, gettext

from ....services.snippet.dbmodels import DbSnippetVersion
from ....services.snippet import snippet_service
from ....services.snippet.transfer.models import Scope
from ....services.text_diff import text_diff_service
from ....services.user import user_service
from ....signals import snippet as snippet_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.iterables import pairwise
from ....util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
)

from ...site.snippet.templating import get_rendered_snippet_body

from .forms import CreateForm, UpdateForm
from .helpers import (
    find_brand_for_scope,
    find_site_for_scope,
    find_snippet_by_id,
    find_snippet_version,
)


blueprint = create_blueprint('snippet_admin', __name__)


@blueprint.get('/for_scope/<scope_type>/<scope_name>')
@permission_required('snippet.view')
@templated
def index_for_scope(scope_type, scope_name):
    """List snippets for that scope."""
    scope = Scope(scope_type, scope_name)

    snippets = snippet_service.get_snippets_for_scope_with_current_versions(
        scope
    )

    user_ids = {snippet.current_version.creator_id for snippet in snippets}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippets': snippets,
        'users_by_id': users_by_id,
        'brand': brand,
        'site': site,
    }


@blueprint.get('/snippets/<uuid:snippet_id>/current_version')
@permission_required('snippet.view')
def view_current_version(snippet_id):
    """Show the current version of the snippet."""
    snippet = find_snippet_by_id(snippet_id)

    version = snippet.current_version

    return view_version(version.id)


@blueprint.get('/versions/<uuid:snippet_version_id>')
@permission_required('snippet.view_history')
@templated
def view_version(snippet_version_id):
    """Show the snippet with the given id."""
    version = find_snippet_version(snippet_version_id)

    snippet = version.snippet
    scope = snippet.scope
    creator = user_service.get_user(version.creator_id, include_avatar=True)
    is_current_version = version.id == snippet.current_version.id

    return {
        'snippet': version.snippet,
        'version': version,
        'scope': scope,
        'creator': creator,
        'brand': find_brand_for_scope(scope),
        'site': find_site_for_scope(scope),
        'is_current_version': is_current_version,
    }


@blueprint.get('/versions/<uuid:snippet_version_id>/preview')
@permission_required('snippet.view_history')
@templated
def view_version_preview(snippet_version_id):
    """Show a preview of the snippet with the given id."""
    version = find_snippet_version(snippet_version_id)

    try:
        body = get_rendered_snippet_body(version)

        return {
            'body': body,
            'error_occurred': False,
        }
    except Exception as e:
        return {
            'error_occurred': True,
            'error_message': str(e),
        }


@blueprint.get('/snippets/<uuid:snippet_id>/history')
@permission_required('snippet.view_history')
@templated
def history(snippet_id):
    snippet = find_snippet_by_id(snippet_id)

    scope = snippet.scope

    versions = snippet_service.get_versions(snippet.id)
    versions_pairwise = list(pairwise(versions + [None]))

    user_ids = {version.creator_id for version in versions}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippet': snippet,
        'versions_pairwise': versions_pairwise,
        'users_by_id': users_by_id,
        'brand': brand,
        'site': site,
    }


@blueprint.get('/for_scope/<scope_type>/<scope_name>/create')
@permission_required('snippet.create')
@templated
def create_form(scope_type, scope_name, erroneous_form=None):
    """Show form to create a snippet."""
    scope = Scope(scope_type, scope_name)

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_language_code_choices()

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'brand': brand,
        'site': site,
    }


@blueprint.post('/for_scope/<scope_type>/<scope_name>')
@permission_required('snippet.create')
def create(scope_type, scope_name):
    """Create a snippet."""
    scope = Scope(scope_type, scope_name)

    form = CreateForm(request.form)
    form.set_language_code_choices()

    if not form.validate():
        return create_form(scope_type, scope_name, form)

    name = form.name.data.strip().lower()
    language_code = form.language_code.data
    creator = g.user
    body = form.body.data.strip()

    version, event = snippet_service.create_snippet(
        scope, name, language_code, creator.id, body
    )

    flash_success(
        gettext(
            'Snippet "%(name)s" has been created.', name=version.snippet.name
        )
    )

    snippet_signals.snippet_created.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.get('/snippets/<uuid:snippet_id>/update')
@permission_required('snippet.update')
@templated
def update_form(snippet_id):
    """Show form to update a snippet."""
    snippet = find_snippet_by_id(snippet_id)
    current_version = snippet.current_version

    scope = snippet.scope

    form = UpdateForm(obj=current_version, name=snippet.name)

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'snippet': snippet,
        'brand': brand,
        'site': site,
    }


@blueprint.post('/snippets/<uuid:snippet_id>')
@permission_required('snippet.update')
def update(snippet_id):
    """Update a snippet."""
    form = UpdateForm(request.form)

    snippet = find_snippet_by_id(snippet_id)

    creator = g.user
    body = form.body.data.strip()

    version, event = snippet_service.update_snippet(
        snippet.id, creator.id, body
    )

    flash_success(
        gettext(
            'Snippet "%(name)s" has been updated.',
            name=version.snippet.name,
        )
    )

    snippet_signals.snippet_updated.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.get(
    '/versions/<uuid:from_version_id>/compare_to/<uuid:to_version_id>'
)
@permission_required('snippet.view_history')
@templated
def compare_versions(from_version_id, to_version_id):
    """Show the difference between two snippet versions."""
    from_version = find_snippet_version(from_version_id)
    to_version = find_snippet_version(to_version_id)

    snippet = from_version.snippet
    scope = snippet.scope

    if from_version.snippet_id != to_version.snippet_id:
        abort(400, 'The versions do not belong to the same snippet.')

    html_diff_body = _create_html_diff(from_version, to_version, 'body')

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'snippet': snippet,
        'scope': scope,
        'diff_body': html_diff_body,
        'brand': brand,
        'site': site,
    }


@blueprint.delete('/snippets/<uuid:snippet_id>')
@permission_required('snippet.delete')
@respond_no_content_with_location
def delete_snippet(snippet_id):
    """Delete a snippet."""
    snippet = find_snippet_by_id(snippet_id)

    snippet_name = snippet.name
    scope = snippet.scope

    success, event = snippet_service.delete_snippet(
        snippet.id, initiator_id=g.user.id
    )

    if not success:
        flash_error(
            gettext(
                'Snippet "%(snippet_name)s" could not be deleted. Is it still mounted?',
                snippet_name=snippet_name,
            )
        )
        return url_for('.view_current_version', snippet_id=snippet.id)

    flash_success(
        gettext('Snippet "%(name)s" has been deleted.', name=snippet_name)
    )
    snippet_signals.snippet_deleted.send(None, event=event)
    return url_for(
        '.index_for_scope', scope_type=scope.type_, scope_name=scope.name
    )


def _create_html_diff(
    from_version: DbSnippetVersion,
    to_version: DbSnippetVersion,
    attribute_name: str,
) -> Optional[str]:
    """Create an HTML diff between the named attribute's value of each
    of the two versions.
    """
    from_description = format_datetime(from_version.created_at)
    to_description = format_datetime(to_version.created_at)

    from_text = getattr(from_version, attribute_name)
    to_text = getattr(to_version, attribute_name)

    return text_diff_service.create_html_diff(
        from_text, to_text, from_description, to_description
    )
