"""
byceps.services.snippet.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request, url_for
from flask_babel import format_datetime, gettext

from byceps.services.snippet import snippet_service, signals as snippet_signals
from byceps.services.snippet.blueprints.site.templating import (
    get_rendered_snippet_body,
)
from byceps.services.snippet.dbmodels import DbSnippetVersion
from byceps.services.snippet.errors import (
    SnippetAlreadyExistsError,
    SnippetNotFoundError,
)
from byceps.services.snippet.models import SnippetScope
from byceps.services.text_diff import text_diff_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.iterables import pairwise
from byceps.util.result import Err, Ok
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
)

from .forms import CopySnippetsForm, CreateForm, UpdateForm
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
    scope = SnippetScope(scope_type, scope_name)

    snippets = snippet_service.get_snippets_for_scope_with_current_versions(
        scope
    )

    user_ids = {snippet.current_version.creator_id for snippet in snippets}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

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
    """Show the snippet with the given ID."""
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
    """Show a preview of the snippet with the given ID."""
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
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

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


@blueprint.get('/for_scope/<target_scope_type>/<target_scope_name>/copy')
@permission_required('snippet.create')
@templated
def copy_select_source_scope_form(
    target_scope_type: str, target_scope_name: str
):
    """Show form to select a scope to copy snippets from."""
    target_scope = SnippetScope(target_scope_type, target_scope_name)

    source_scopes = [
        scope
        for scope in snippet_service.get_all_scopes()
        if scope != target_scope
    ]
    source_scopes.sort(key=lambda scope: (scope.type_, scope.name))

    scope = target_scope
    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'scope': scope,
        'target_scope': target_scope,
        'source_scopes': source_scopes,
        'brand': brand,
        'site': site,
    }


@blueprint.get(
    '/for_scope/<target_scope_type>/<target_scope_name>/copy/from_scope/<source_scope_type>/<source_scope_name>'
)
@permission_required('snippet.create')
@templated
def copy_form(
    target_scope_type: str,
    target_scope_name: str,
    source_scope_type: str,
    source_scope_name: str,
    erroneous_form=None,
):
    """Show form to select snippets to copy from another scope."""
    source_scope = SnippetScope(source_scope_type, source_scope_name)
    target_scope = SnippetScope(target_scope_type, target_scope_name)

    snippets = snippet_service.get_snippets_for_scope_with_current_versions(
        source_scope
    )
    if not snippets:
        flash_error('No snippets exist for this scope.')
        return redirect_to(
            '.copy_select_source_scope_form',
            target_scope_type=target_scope_type,
            target_scope_name=target_scope_name,
        )

    form = erroneous_form if erroneous_form else CopySnippetsForm()
    form.set_source_snippet_id_choices(snippets)

    scope = target_scope
    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    return {
        'form': form,
        'scope': scope,
        'target_scope': target_scope,
        'source_scope': source_scope,
        'brand': brand,
        'site': site,
    }


@blueprint.post(
    '/for_scope/<target_scope_type>/<target_scope_name>/copy/from_scope/<source_scope_type>/<source_scope_name>'
)
@permission_required('snippet.create')
def copy(
    target_scope_type: str,
    target_scope_name: str,
    source_scope_type: str,
    source_scope_name: str,
):
    """Copy snippets from another scope."""
    source_scope = SnippetScope(source_scope_type, source_scope_name)
    target_scope = SnippetScope(target_scope_type, target_scope_name)

    snippets = snippet_service.get_snippets_for_scope_with_current_versions(
        source_scope
    )
    if not snippets:
        flash_error('No snippets exist for this scope.')
        return redirect_to(
            '.copy_select_source_scope_form',
            target_scope_type=target_scope_type,
            target_scope_name=target_scope_name,
        )

    form = CopySnippetsForm(request.form)
    form.set_source_snippet_id_choices(snippets)

    if not form.validate():
        return copy_form(
            target_scope.type_,
            target_scope.name,
            source_scope.type_,
            source_scope.name,
            form,
        )

    for snippet_id in form.source_snippet_ids.data:
        snippet = snippet_service.find_snippet(snippet_id)
        if snippet is None:
            flash_error(
                gettext(
                    'Unknown snippet ID "%(snippet_id)s"', snippet_id=snippet_id
                )
            )
            continue

        result = snippet_service.copy_snippet(
            source_scope, target_scope, snippet.name, snippet.language_code
        )
        match result:
            case Ok((_, event)):
                flash_success(
                    gettext(
                        'Snippet "%(name)s" (%(language_code)s) has been copied.',
                        name=snippet.name,
                        language_code=snippet.language_code,
                    )
                )
                snippet_signals.snippet_created.send(None, event=event)
            case Err(SnippetNotFoundError()):
                flash_error(
                    gettext(
                        'Snippet "%(name)s" (%(language_code)s) was not found in scope "%(source_scope)s".',
                        name=snippet.name,
                        language_code=snippet.language_code,
                        source_scope=source_scope.as_string(),
                    )
                )
            case Err(SnippetAlreadyExistsError()):
                flash_error(
                    gettext(
                        'Snippet "%(name)s" (%(language_code)s) already exists in scope "%(target_scope)s".',
                        name=snippet.name,
                        language_code=snippet.language_code,
                        target_scope=target_scope.as_string(),
                    )
                )

    return redirect_to(
        '.index_for_scope',
        scope_type=target_scope.type_,
        scope_name=target_scope.name,
    )


@blueprint.get('/for_scope/<scope_type>/<scope_name>/create')
@permission_required('snippet.create')
@templated
def create_form(scope_type, scope_name, erroneous_form=None):
    """Show form to create a snippet."""
    scope = SnippetScope(scope_type, scope_name)

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
    scope = SnippetScope(scope_type, scope_name)

    form = CreateForm(request.form)
    form.set_language_code_choices()

    if not form.validate():
        return create_form(scope_type, scope_name, form)

    name = form.name.data.strip().lower()
    language_code = form.language_code.data
    creator = g.user
    body = form.body.data.strip()

    version, event = snippet_service.create_snippet(
        scope, name, language_code, creator, body
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

    version, event = snippet_service.update_snippet(snippet.id, creator, body)

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

    match snippet_service.delete_snippet(snippet.id, initiator=g.user):
        case Ok(event):
            flash_success(
                gettext(
                    'Snippet "%(name)s" has been deleted.', name=snippet_name
                )
            )
            snippet_signals.snippet_deleted.send(None, event=event)
            return url_for(
                '.index_for_scope',
                scope_type=scope.type_,
                scope_name=scope.name,
            )
        case Err(_):
            flash_error(
                gettext(
                    'Snippet "%(snippet_name)s" could not be deleted. Is it still mounted?',
                    snippet_name=snippet_name,
                )
            )
            return url_for('.view_current_version', snippet_id=snippet.id)


def _create_html_diff(
    from_version: DbSnippetVersion,
    to_version: DbSnippetVersion,
    attribute_name: str,
) -> str | None:
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
