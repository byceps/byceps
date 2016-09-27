# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import abort, g, render_template, request, url_for

from ...util.dateformat import format_datetime_short
from ...util.framework import create_blueprint, flash_success
from ...util.iterables import pairwise
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party import service as party_service
from ..snippet import service as snippet_service
from ..snippet.templating import get_snippet_context

from .authorization import MountpointPermission, SnippetPermission
from .forms import MountpointCreateForm, SnippetCreateForm, SnippetUpdateForm
from . import service


blueprint = create_blueprint('snippet_admin', __name__)


permission_registry.register_enum(MountpointPermission)
permission_registry.register_enum(SnippetPermission)


@blueprint.route('/<party_id>')
@permission_required(SnippetPermission.list)
@templated
def index_for_party(party_id):
    """List snippets for that party."""
    party = _get_party_or_404(party_id)

    snippets = service.get_snippets_for_party_with_current_versions(party)

    mountpoints = snippet_service.get_mountpoints_for_party(party)

    return {
        'party': party,
        'snippets': snippets,
        'mountpoints': mountpoints,
    }


@blueprint.route('/versions/<uuid:snippet_version_id>')
@permission_required(SnippetPermission.view_history)
def view_version(snippet_version_id):
    """Show the snippet with the given id."""
    version = find_version(snippet_version_id)

    try:
        snippet_context = get_snippet_context(version)

        context = {
            'party': version.snippet.party,
            'snippet_title': snippet_context['title'],
            'snippet_head': snippet_context['head'],
            'snippet_body': snippet_context['body'],
        }

        return render_template('snippet_admin/view_version.html', **context)
    except Exception as e:
        context = {
            'party': version.snippet.party,
            'error_message': str(e),
        }

        return render_template('snippet_admin/view_version_error.html',
                               **context), \
               500


@blueprint.route('/difference/from/<uuid:from_version_id>/to/<uuid:to_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def view_difference(from_version_id, to_version_id):
    """Show the difference between two snippet versions."""
    from_version = find_version(from_version_id)
    to_version = find_version(to_version_id)

    # TODO: Diff title, head, and image path, too.

    from_description = format_datetime_short(from_version.created_at)
    to_description = format_datetime_short(to_version.created_at)

    def create_html_diff(from_text, to_text):
        return service.create_html_diff(from_text, to_text,
                                        from_description, to_description)

    html_diff_title = create_html_diff(from_version.title, to_version.title)

    html_diff_head = create_html_diff(from_version.head, to_version.head)

    html_diff_body = create_html_diff(from_version.body, to_version.body)

    html_diff_image_url_path = create_html_diff(from_version.image_url_path,
                                                to_version.image_url_path)

    return {
        'diff_title': html_diff_title,
        'diff_head': html_diff_head,
        'diff_body': html_diff_body,
        'diff_image_url_path': html_diff_image_url_path,
    }


@blueprint.route('/<uuid:snippet_id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(snippet_id):
    snippet = find_snippet_by_id(snippet_id)

    versions = snippet.get_versions()
    versions_pairwise = list(pairwise(versions + [None]))

    return {
        'snippet': snippet,
        'versions_pairwise': versions_pairwise,
    }


@blueprint.route('/for_party/<party_id>/create')
@permission_required(SnippetPermission.create)
@templated
def create_snippet_form(party_id):
    """Show form to create a snippet."""
    party = _get_party_or_404(party_id)

    form = SnippetCreateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/for_party/<party_id>', methods=['POST'])
@permission_required(SnippetPermission.create)
def create_snippet(party_id):
    """Create a snippet."""
    party = _get_party_or_404(party_id)

    form = SnippetCreateForm(request.form)

    name = form.name.data.strip().lower()

    creator = g.current_user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    version = snippet_service.create_snippet(party, name, creator, title, head,
                                             body, image_url_path)

    flash_success('Das Snippet "{}" wurde angelegt.', version.snippet.name)
    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/snippets/<uuid:snippet_id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_snippet_form(snippet_id):
    """Show form to update a snippet."""
    snippet = find_snippet_by_id(snippet_id)
    current_version = snippet.current_version

    form = SnippetUpdateForm(
        obj=current_version,
        name=snippet.name)

    return {
        'form': form,
        'snippet': snippet,
    }


@blueprint.route('/snippets/<uuid:snippet_id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_snippet(snippet_id):
    """Update a snippet."""
    form = SnippetUpdateForm(request.form)

    snippet = find_snippet_by_id(snippet_id)

    creator = g.current_user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    version = snippet_service.update_snippet(snippet, creator, title, head,
                                             body, image_url_path)

    flash_success('Das Snippet "{}" wurde aktualisiert.', version.snippet.name)
    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/mointpoints/for_party/<party_id>/create')
@permission_required(MountpointPermission.create)
@templated
def create_mountpoint_form(party_id):
    """Show form to create a mountpoint."""
    party = _get_party_or_404(party_id)

    snippets = service.get_snippets_for_party(party)
    snippet_choices = list(map(attrgetter('id', 'name'), snippets))

    form = MountpointCreateForm()
    form.snippet_id.choices = snippet_choices

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/mountpoints/for_party/<party_id>', methods=['POST'])
@permission_required(MountpointPermission.create)
def create_mountpoint(party_id):
    """Create a mountpoint."""
    party = _get_party_or_404(party_id)

    form = MountpointCreateForm(request.form)

    endpoint_suffix = form.endpoint_suffix.data.strip()
    url_path = form.url_path.data.strip()
    if not url_path.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    snippet_id = form.snippet_id.data.strip().lower()
    snippet = find_snippet_by_id(snippet_id)

    mountpoint = snippet_service.create_mountpoint(endpoint_suffix, url_path,
                                                   snippet)

    flash_success('Der Mountpoint für "{}" wurde angelegt.',
                  mountpoint.url_path)
    return redirect_to('.index_for_party', party_id=party.id)


@blueprint.route('/mountpoints/<uuid:mountpoint_id>', methods=['DELETE'])
@permission_required(MountpointPermission.delete)
@respond_no_content_with_location
def delete_mountpoint(mountpoint_id):
    """Delete a mountpoint."""
    mountpoint = snippet_service.find_mountpoint(mountpoint_id)
    if mountpoint is None:
        abort(404)

    url_path = mountpoint.url_path
    party = mountpoint.snippet.party

    snippet_service.delete_mountpoint(mountpoint)

    flash_success('Der Mountpoint für "{}" wurde entfernt.', url_path)
    return url_for('.index_for_party', party_id=party.id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def find_snippet_by_id(snippet_id):
    snippet = snippet_service.find_snippet(snippet_id)

    if snippet is None:
        abort(404)

    return snippet


def find_version(version_id):
    version = snippet_service.find_snippet_version(version_id)

    if version is None:
        abort(404)

    return version
