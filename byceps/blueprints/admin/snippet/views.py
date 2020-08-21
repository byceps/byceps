"""
byceps.blueprints.admin.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request, url_for

from ....services.brand import service as brand_service
from ....services.site import service as site_service
from ....services.snippet import mountpoint_service, service as snippet_service
from ....services.snippet.transfer.models import Scope
from ....services.text_diff import service as text_diff_service
from ....signals import snippet as snippet_signals
from ....util.datetime.format import format_datetime_short
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.iterables import pairwise
from ....util.framework.templating import templated
from ....util.views import (
    redirect_to,
    respond_no_content,
    respond_no_content_with_location,
)

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry
from ...site.snippet.templating import get_snippet_context

from .authorization import SnippetMountpointPermission, SnippetPermission
from .forms import (
    DocumentCreateForm,
    DocumentUpdateForm,
    FragmentCreateForm,
    FragmentUpdateForm,
    MountpointCreateForm,
)

blueprint = create_blueprint('snippet_admin', __name__)


permission_registry.register_enum(SnippetMountpointPermission)
permission_registry.register_enum(SnippetPermission)


@blueprint.route('/for_scope/<scope_type>/<scope_name>')
@permission_required(SnippetPermission.view)
@templated
def index_for_scope(scope_type, scope_name):
    """List snippets for that scope."""
    scope = Scope(scope_type, scope_name)

    snippets = snippet_service.get_snippets_for_scope_with_current_versions(
        scope
    )

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippets': snippets,
        'brand': brand,
        'site': site,
    }


@blueprint.route('/snippets/<uuid:snippet_id>/current_version')
@permission_required(SnippetPermission.view)
def view_current_version(snippet_id):
    """Show the current version of the snippet."""
    snippet = _find_snippet_by_id(snippet_id)

    version = snippet.current_version

    return view_version(version.id)


@blueprint.route('/versions/<uuid:snippet_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def view_version(snippet_version_id):
    """Show the snippet with the given id."""
    version = _find_version(snippet_version_id)

    snippet = version.snippet
    scope = snippet.scope
    is_current_version = version.id == snippet.current_version.id

    context = {
        'scope': scope,
        'brand': _find_brand_for_scope(scope),
        'site': _find_site_for_scope(scope),
        'is_current_version': is_current_version,
    }

    try:
        snippet_context = get_snippet_context(version)

        extra_context = {
            'version': version,
            'snippet_title': snippet_context['title'],
            'snippet_head': snippet_context['head'],
            'snippet_body': snippet_context['body'],
            'error_occurred': False,
        }
    except Exception as e:
        extra_context = {
            'version': version,
            'error_occurred': True,
            'error_message': str(e),
        }

    context.update(extra_context)

    return context


@blueprint.route('/snippets/<uuid:snippet_id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(snippet_id):
    snippet = _find_snippet_by_id(snippet_id)

    scope = snippet.scope

    versions = snippet_service.get_versions(snippet.id)
    versions_pairwise = list(pairwise(versions + [None]))

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippet': snippet,
        'versions_pairwise': versions_pairwise,
        'brand': brand,
        'site': site,
    }


# -------------------------------------------------------------------- #
# document


@blueprint.route('/for_scope/<scope_type>/<scope_name>/documents/create')
@permission_required(SnippetPermission.create)
@templated
def create_document_form(scope_type, scope_name):
    """Show form to create a document."""
    scope = Scope(scope_type, scope_name)

    form = DocumentCreateForm()

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'brand': brand,
        'site': site,
    }


@blueprint.route(
    '/for_scope/<scope_type>/<scope_name>/documents', methods=['POST']
)
@permission_required(SnippetPermission.create)
def create_document(scope_type, scope_name):
    """Create a document."""
    scope = Scope(scope_type, scope_name)

    form = DocumentCreateForm(request.form)

    name = form.name.data.strip().lower()
    creator = g.current_user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    version, event = snippet_service.create_document(
        scope,
        name,
        creator.id,
        title,
        body,
        head=head,
        image_url_path=image_url_path,
    )

    flash_success(f'Das Dokument "{version.snippet.name}" wurde angelegt.')

    snippet_signals.snippet_created.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/documents/<uuid:snippet_id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_document_form(snippet_id):
    """Show form to update a document."""
    snippet = _find_snippet_by_id(snippet_id)
    current_version = snippet.current_version

    scope = snippet.scope

    form = DocumentUpdateForm(obj=current_version, name=snippet.name)

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'snippet': snippet,
        'brand': brand,
        'site': site,
    }


@blueprint.route('/documents/<uuid:snippet_id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_document(snippet_id):
    """Update a document."""
    form = DocumentUpdateForm(request.form)

    snippet = _find_snippet_by_id(snippet_id)

    creator = g.current_user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    version, event = snippet_service.update_document(
        snippet.id,
        creator.id,
        title,
        body,
        head=head,
        image_url_path=image_url_path,
    )

    flash_success(f'Das Dokument "{version.snippet.name}" wurde aktualisiert.')

    snippet_signals.snippet_updated.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route(
    '/documents/<uuid:from_version_id>/compare_to/<uuid:to_version_id>'
)
@permission_required(SnippetPermission.view_history)
@templated
def compare_documents(from_version_id, to_version_id):
    """Show the difference between two document versions."""
    from_version = _find_version(from_version_id)
    to_version = _find_version(to_version_id)

    scope = from_version.snippet.scope

    if from_version.snippet_id != to_version.snippet_id:
        abort(400, 'The versions do not belong to the same snippet.')

    html_diff_title = _create_html_diff(from_version, to_version, 'title')
    html_diff_head = _create_html_diff(from_version, to_version, 'head')
    html_diff_body = _create_html_diff(from_version, to_version, 'body')
    html_diff_image_url_path = _create_html_diff(
        from_version, to_version, 'image_url_path'
    )

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'diff_title': html_diff_title,
        'diff_head': html_diff_head,
        'diff_body': html_diff_body,
        'diff_image_url_path': html_diff_image_url_path,
        'brand': brand,
        'site': site,
    }


# -------------------------------------------------------------------- #
# fragment


@blueprint.route('/for_scope/<scope_type>/<scope_name>/fragments/create')
@permission_required(SnippetPermission.create)
@templated
def create_fragment_form(scope_type, scope_name):
    """Show form to create a fragment."""
    scope = Scope(scope_type, scope_name)

    form = FragmentCreateForm()

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'brand': brand,
        'site': site,
    }


@blueprint.route(
    '/for_scope/<scope_type>/<scope_name>/fragments', methods=['POST']
)
@permission_required(SnippetPermission.create)
def create_fragment(scope_type, scope_name):
    """Create a fragment."""
    scope = Scope(scope_type, scope_name)

    form = FragmentCreateForm(request.form)

    name = form.name.data.strip().lower()
    creator = g.current_user
    body = form.body.data.strip()

    version, event = snippet_service.create_fragment(
        scope, name, creator.id, body
    )

    flash_success(f'Das Fragment "{version.snippet.name}" wurde angelegt.')

    snippet_signals.snippet_created.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/fragments/<uuid:snippet_id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_fragment_form(snippet_id):
    """Show form to update a fragment."""
    snippet = _find_snippet_by_id(snippet_id)
    current_version = snippet.current_version

    scope = snippet.scope

    form = FragmentUpdateForm(obj=current_version, name=snippet.name)

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'snippet': snippet,
        'brand': brand,
        'site': site,
    }


@blueprint.route('/fragments/<uuid:snippet_id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_fragment(snippet_id):
    """Update a fragment."""
    form = FragmentUpdateForm(request.form)

    snippet = _find_snippet_by_id(snippet_id)

    creator = g.current_user
    body = form.body.data.strip()

    version, event = snippet_service.update_fragment(
        snippet.id, creator.id, body
    )

    flash_success(f'Das Fragment "{version.snippet.name}" wurde aktualisiert.')

    snippet_signals.snippet_updated.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route(
    '/fragments/<uuid:from_version_id>/compare_to/<uuid:to_version_id>'
)
@permission_required(SnippetPermission.view_history)
@templated
def compare_fragments(from_version_id, to_version_id):
    """Show the difference between two fragment versions."""
    from_version = _find_version(from_version_id)
    to_version = _find_version(to_version_id)

    scope = from_version.snippet.scope

    if from_version.snippet_id != to_version.snippet_id:
        abort(400, 'The versions do not belong to the same snippet.')

    html_diff_body = _create_html_diff(from_version, to_version, 'body')

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'diff_body': html_diff_body,
        'brand': brand,
        'site': site,
    }


# -------------------------------------------------------------------- #
# delete


@blueprint.route('/snippets/<uuid:snippet_id>', methods=['DELETE'])
@permission_required(SnippetPermission.delete)
@respond_no_content_with_location
def delete_snippet(snippet_id):
    """Delete a snippet."""
    snippet = _find_snippet_by_id(snippet_id)

    snippet_name = snippet.name
    scope = snippet.scope

    success, event = snippet_service.delete_snippet(
        snippet.id, initiator_id=g.current_user.id
    )

    if not success:
        flash_error(
            f'Das Snippet "{snippet_name}" konnte nicht gelöscht werden. '
            'Ist es noch gemountet?'
        )
        return url_for('.view_current_version', snippet_id=snippet.id)

    flash_success(f'Das Snippet "{snippet_name}" wurde gelöscht.')
    snippet_signals.snippet_deleted.send(None, event=event)
    return url_for(
        '.index_for_scope', scope_type=scope.type_, scope_name=scope.name
    )


# -------------------------------------------------------------------- #
# mountpoint


@blueprint.route('/mountpoints/<site_id>')
@permission_required(SnippetPermission.view)
@templated
def index_mountpoints(site_id):
    """List mountpoints for that site."""
    scope = Scope.for_site(site_id)

    mountpoints = mountpoint_service.get_mountpoints_for_site(site_id)

    snippet_ids = {mp.snippet_id for mp in mountpoints}
    snippets = snippet_service.get_snippets(snippet_ids)
    snippets_by_snippet_id = {snippet.id: snippet for snippet in snippets}

    mountpoints_and_snippets = [
        (mp, snippets_by_snippet_id[mp.snippet_id]) for mp in mountpoints
    ]

    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'mountpoints_and_snippets': mountpoints_and_snippets,
        'site': site,
    }


@blueprint.route('/snippets/<uuid:snippet_id>/mountpoints/create')
@permission_required(SnippetMountpointPermission.create)
@templated
def create_mountpoint_form(snippet_id, *, erroneous_form=None):
    """Show form to create a mountpoint."""
    snippet = _find_snippet_by_id(snippet_id)

    scope = snippet.scope

    form = erroneous_form if erroneous_form else MountpointCreateForm()

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippet': snippet,
        'form': form,
        'brand': brand,
        'site': site,
    }


@blueprint.route('/snippets/<uuid:snippet_id>/mountpoints', methods=['POST'])
@permission_required(SnippetMountpointPermission.create)
def create_mountpoint(snippet_id):
    """Create a mountpoint."""
    snippet = _find_snippet_by_id(snippet_id)

    form = MountpointCreateForm(request.form)
    if not form.validate():
        return create_mountpoint_form(snippet.id, erroneous_form=form)

    site_id = form.site_id.data
    endpoint_suffix = form.endpoint_suffix.data.strip()
    url_path = form.url_path.data.strip()

    mountpoint = mountpoint_service.create_mountpoint(
        site_id, endpoint_suffix, url_path, snippet.id
    )

    flash_success(f'Der Mountpoint für "{mountpoint.url_path}" wurde angelegt.')
    return redirect_to('.index_mountpoints', site_id=site_id)


@blueprint.route('/mountpoints/<uuid:mountpoint_id>', methods=['DELETE'])
@permission_required(SnippetMountpointPermission.delete)
@respond_no_content
def delete_mountpoint(mountpoint_id):
    """Delete a mountpoint."""
    mountpoint = mountpoint_service.find_mountpoint(mountpoint_id)

    if mountpoint is None:
        abort(404)

    url_path = mountpoint.url_path

    mountpoint_service.delete_mountpoint(mountpoint.id)

    flash_success(f'Der Mountpoint für "{url_path}" wurde entfernt.')


# -------------------------------------------------------------------- #
# helpers


def _find_snippet_by_id(snippet_id):
    snippet = snippet_service.find_snippet(snippet_id)

    if snippet is None:
        abort(404)

    return snippet


def _find_version(version_id):
    version = snippet_service.find_snippet_version(version_id)

    if version is None:
        abort(404)

    return version


def _create_html_diff(from_version, to_version, attribute_name):
    """Create an HTML diff between the named attribute's value of each
    of the two versions.
    """
    from_description = format_datetime_short(from_version.created_at)
    to_description = format_datetime_short(to_version.created_at)

    from_text = getattr(from_version, attribute_name)
    to_text = getattr(to_version, attribute_name)

    return text_diff_service.create_html_diff(
        from_text, to_text, from_description, to_description
    )


def _find_brand_for_scope(scope):
    if scope.type_ != 'brand':
        return None

    return brand_service.find_brand(scope.name)


def _find_site_for_scope(scope):
    if scope.type_ != 'site':
        return None

    return site_service.find_site(scope.name)
