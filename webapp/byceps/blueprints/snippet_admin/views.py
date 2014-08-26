# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import abort, g, redirect, request, url_for

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..snippet.models import Snippet, SnippetVersion
from ..snippet.templating import render_snippet

from .authorization import SnippetPermission
from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('snippet_admin', __name__)


permission_registry.register_enum(SnippetPermission)


@blueprint.route('/')
@permission_required(SnippetPermission.list)
@templated
def index():
    """List snippets."""
    snippets = Snippet.query.for_current_party().all()
    return {'snippets': snippets}


@blueprint.route('/versions/<id>')
@permission_required(SnippetPermission.view_history)
def view_version(id):
    """Show the snippet with the given id."""
    version = find_version(id)
    return render_snippet(version)


@blueprint.route('/<id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(id):
    snippet = find_snippet_by_id(id)
    return {
        'snippet': snippet,
    }


@blueprint.route('/create')
@permission_required(SnippetPermission.create)
@templated
def create_form():
    """Show form to create a snippet."""
    form = CreateForm()
    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
@permission_required(SnippetPermission.create)
def create():
    """Create a snippet."""
    form = CreateForm(request.form)

    name = form.name.data.strip()
    url_path = form.url_path.data.strip()
    if not url_path.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    snippet = Snippet(
        name=name,
        party=g.party,
        url_path=url_path)
    db.session.add(snippet)

    version = SnippetVersion(
        snippet=snippet,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)

    db.session.commit()

    flash_success('Das Snippet "{}" wurde angelegt.', snippet.name)
    return redirect(url_for('.view_version', id=version.id))


@blueprint.route('/<id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_form(id):
    """Show form to update a snippet."""
    snippet = find_snippet_by_id(id)
    latest_version = snippet.get_latest_version()

    form = UpdateForm(
        obj=snippet,
        title=latest_version.title,
        body=latest_version.body)

    return {
        'form': form,
        'snippet': snippet,
    }


@blueprint.route('/<id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update(id):
    """Update a snippet."""
    form = UpdateForm(request.form)

    snippet = find_snippet_by_id(id)

    version = SnippetVersion(
        snippet=snippet,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)
    db.session.commit()

    flash_success('Das Snippet "{}" wurde aktualisiert.', snippet.name)
    return redirect(url_for('.view_version', id=version.id))


def find_snippet_by_id(id):
    return Snippet.query.get_or_404(id)


def find_version(id):
    return SnippetVersion.query.get_or_404(id)
