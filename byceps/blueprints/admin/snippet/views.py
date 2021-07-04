"""
byceps.blueprints.admin.snippet.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional
from flask import abort, g, request, url_for
from flask_babel import gettext

from ....services.brand import service as brand_service
from ....services.brand.transfer.models import Brand
from ....services.site import service as site_service
from ....services.site.transfer.models import Site, SiteID
from ....services.snippet.dbmodels.snippet import (
    Snippet as DbSnippet,
    SnippetVersion as DbSnippetVersion,
)
from ....services.snippet import mountpoint_service, service as snippet_service
from ....services.snippet.transfer.models import (
    Scope,
    SnippetID,
    SnippetVersionID,
)
from ....services.text_diff import service as text_diff_service
from ....services.user import service as user_service
from ....signals import snippet as snippet_signals
from ....util.authorization import register_permission_enum
from ....util.datetime.format import format_datetime_short
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.iterables import pairwise
from ....util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
    respond_no_content_with_location,
)
from ....typing import BrandID

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


register_permission_enum(SnippetMountpointPermission)
register_permission_enum(SnippetPermission)


@blueprint.get('/for_scope/<scope_type>/<scope_name>')
@permission_required(SnippetPermission.view)
@templated
def index_for_scope(scope_type, scope_name):
    """List snippets for that scope."""
    scope = Scope(scope_type, scope_name)

    snippets = snippet_service.get_snippets_for_scope_with_current_versions(
        scope
    )

    user_ids = {snippet.current_version.creator_id for snippet in snippets}
    users = user_service.find_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippets': snippets,
        'users_by_id': users_by_id,
        'brand': brand,
        'site': site,
    }


@blueprint.get('/snippets/<uuid:snippet_id>/current_version')
@permission_required(SnippetPermission.view)
def view_current_version(snippet_id):
    """Show the current version of the snippet."""
    snippet = _find_snippet_by_id(snippet_id)

    version = snippet.current_version

    return view_version(version.id)


@blueprint.get('/versions/<uuid:snippet_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def view_version(snippet_version_id):
    """Show the snippet with the given id."""
    version = _find_version(snippet_version_id)

    snippet = version.snippet
    scope = snippet.scope
    creator = user_service.get_user(version.creator_id, include_avatar=True)
    is_current_version = version.id == snippet.current_version.id

    context = {
        'version': version,
        'scope': scope,
        'creator': creator,
        'brand': _find_brand_for_scope(scope),
        'site': _find_site_for_scope(scope),
        'is_current_version': is_current_version,
    }

    try:
        snippet_context = get_snippet_context(version)

        extra_context = {
            'snippet_title': snippet_context['page_title'],
            'snippet_head': snippet_context['head'],
            'snippet_body': snippet_context['body'],
            'error_occurred': False,
        }
    except Exception as e:
        extra_context = {
            'error_occurred': True,
            'error_message': str(e),
        }

    context.update(extra_context)

    return context


@blueprint.get('/snippets/<uuid:snippet_id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(snippet_id):
    snippet = _find_snippet_by_id(snippet_id)

    scope = snippet.scope

    versions = snippet_service.get_versions(snippet.id)
    versions_pairwise = list(pairwise(versions + [None]))

    user_ids = {version.creator_id for version in versions}
    users = user_service.find_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippet': snippet,
        'versions_pairwise': versions_pairwise,
        'users_by_id': users_by_id,
        'brand': brand,
        'site': site,
    }


# -------------------------------------------------------------------- #
# document


@blueprint.get('/for_scope/<scope_type>/<scope_name>/documents/create')
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


@blueprint.post('/for_scope/<scope_type>/<scope_name>/documents')
@permission_required(SnippetPermission.create)
def create_document(scope_type, scope_name):
    """Create a document."""
    scope = Scope(scope_type, scope_name)

    form = DocumentCreateForm(request.form)

    name = form.name.data.strip().lower()
    creator = g.user
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

    flash_success(
        gettext(
            'Document "%(name)s" has been created.', name=version.snippet.name
        )
    )

    snippet_signals.snippet_created.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.get('/documents/<uuid:snippet_id>/update')
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


@blueprint.post('/documents/<uuid:snippet_id>')
@permission_required(SnippetPermission.update)
def update_document(snippet_id):
    """Update a document."""
    form = DocumentUpdateForm(request.form)

    snippet = _find_snippet_by_id(snippet_id)

    creator = g.user
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

    flash_success(
        gettext(
            'Document "%(name)s" has been updated.',
            name=version.snippet.name,
        )
    )

    snippet_signals.snippet_updated.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.get(
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


@blueprint.get('/for_scope/<scope_type>/<scope_name>/fragments/create')
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


@blueprint.post('/for_scope/<scope_type>/<scope_name>/fragments')
@permission_required(SnippetPermission.create)
def create_fragment(scope_type, scope_name):
    """Create a fragment."""
    scope = Scope(scope_type, scope_name)

    form = FragmentCreateForm(request.form)

    name = form.name.data.strip().lower()
    creator = g.user
    body = form.body.data.strip()

    version, event = snippet_service.create_fragment(
        scope, name, creator.id, body
    )

    flash_success(
        gettext(
            'Fragment "%(name)s" has been created.', name=version.snippet.name
        )
    )

    snippet_signals.snippet_created.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.get('/fragments/<uuid:snippet_id>/update')
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


@blueprint.post('/fragments/<uuid:snippet_id>')
@permission_required(SnippetPermission.update)
def update_fragment(snippet_id):
    """Update a fragment."""
    form = FragmentUpdateForm(request.form)

    snippet = _find_snippet_by_id(snippet_id)

    creator = g.user
    body = form.body.data.strip()

    version, event = snippet_service.update_fragment(
        snippet.id, creator.id, body
    )

    flash_success(
        gettext(
            'Fragment "%(name)s" has been updated.',
            name=version.snippet.name,
        )
    )

    snippet_signals.snippet_updated.send(None, event=event)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.get(
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


@blueprint.delete('/snippets/<uuid:snippet_id>')
@permission_required(SnippetPermission.delete)
@respond_no_content_with_location
def delete_snippet(snippet_id):
    """Delete a snippet."""
    snippet = _find_snippet_by_id(snippet_id)

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


# -------------------------------------------------------------------- #
# mountpoint


@blueprint.get('/mountpoints/<site_id>')
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


@blueprint.get('/snippets/<uuid:snippet_id>/mountpoints/create')
@permission_required(SnippetMountpointPermission.create)
@templated
def create_mountpoint_form(snippet_id, *, erroneous_form=None):
    """Show form to create a mountpoint."""
    snippet = _find_snippet_by_id(snippet_id)

    scope = snippet.scope

    brand = _find_brand_for_scope(scope)
    site = _find_site_for_scope(scope)

    sites = _get_sites_to_potentially_mount_to(brand, site)

    form = erroneous_form if erroneous_form else MountpointCreateForm()
    form.set_site_id_choices(sites)

    return {
        'scope': scope,
        'snippet': snippet,
        'form': form,
        'brand': brand,
        'site': site,
    }


def _get_sites_to_potentially_mount_to(
    brand: Optional[Brand] = None, site: Optional[Site] = None
) -> set[Site]:
    if site is not None:
        return {site}
    elif brand is not None:
        return site_service.get_sites_for_brand(brand.id)
    else:
        return site_service.get_all_sites()


@blueprint.post('/snippets/<uuid:snippet_id>/mountpoints')
@permission_required(SnippetMountpointPermission.create)
def create_mountpoint(snippet_id):
    """Create a mountpoint."""
    snippet = _find_snippet_by_id(snippet_id)

    sites = site_service.get_all_sites()

    form = MountpointCreateForm(request.form)
    form.set_site_id_choices(sites)

    if not form.validate():
        return create_mountpoint_form(snippet.id, erroneous_form=form)

    site_id = form.site_id.data
    endpoint_suffix = form.endpoint_suffix.data.strip()
    url_path = form.url_path.data.strip()

    mountpoint = mountpoint_service.create_mountpoint(
        site_id, endpoint_suffix, url_path, snippet.id
    )

    flash_success(
        gettext(
            'Mountpoint for "%(url_path)s" has been created.',
            url_path=mountpoint.url_path,
        )
    )

    return redirect_to('.index_mountpoints', site_id=site_id)


@blueprint.delete('/mountpoints/<uuid:mountpoint_id>')
@permission_required(SnippetMountpointPermission.delete)
@respond_no_content
def delete_mountpoint(mountpoint_id):
    """Delete a mountpoint."""
    mountpoint = mountpoint_service.find_mountpoint(mountpoint_id)

    if mountpoint is None:
        abort(404)

    url_path = mountpoint.url_path

    mountpoint_service.delete_mountpoint(mountpoint.id)

    flash_success(
        gettext(
            'Mountpoint for "%(url_path)s" has been deleted.',
            url_path=url_path,
        )
    )


# -------------------------------------------------------------------- #
# helpers


def _find_snippet_by_id(snippet_id: SnippetID) -> DbSnippet:
    snippet = snippet_service.find_snippet(snippet_id)

    if snippet is None:
        abort(404)

    return snippet


def _find_version(version_id: SnippetVersionID) -> DbSnippetVersion:
    version = snippet_service.find_snippet_version(version_id)

    if version is None:
        abort(404)

    return version


def _create_html_diff(
    from_version: DbSnippetVersion,
    to_version: DbSnippetVersion,
    attribute_name: str,
) -> Optional[str]:
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


def _find_brand_for_scope(scope: Scope) -> Optional[Brand]:
    if scope.type_ != 'brand':
        return None

    return brand_service.find_brand(BrandID(scope.name))


def _find_site_for_scope(scope: Scope) -> Optional[Site]:
    if scope.type_ != 'site':
        return None

    return site_service.find_site(SiteID(scope.name))
