# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import abort, current_app, g, redirect, request, url_for

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import ContentPagePermission
from .forms import CreateForm, UpdateForm
from .models import ContentPage, ContentPageVersion
from .templating import render_page


blueprint = create_blueprint('contentpage', __name__)


permission_registry.register_enum('content_page', ContentPagePermission)


def add_routes_for_pages():
    """Register routes for pages with the application."""
    party_id = current_app.party_id
    pages = ContentPage.query.for_party_with_id(party_id).all()
    for page in pages:
        add_route_for_page(page)


def add_route_for_page(page):
    """Register a route for the page."""
    endpoint = '{}.{}'.format(blueprint.name, page.name)
    defaults = {'name': page.name}
    current_app.add_url_rule(
        page.url_path,
        endpoint,
        view_func=view_latest_by_name,
        defaults=defaults)


@blueprint.route('/')
@permission_required(ContentPagePermission.list)
@templated
def index():
    """List pages."""
    pages = ContentPage.query.for_current_party().all()
    return {'pages': pages}


def view_latest_by_name(name):
    """Show the latest version of the page with the given name."""
    page = ContentPage.query \
        .for_current_party(name) \
        .filter_by(name=name) \
        .one()
    return render_page(page.get_latest_version())


@blueprint.route('/versions/<id>')
@permission_required(ContentPagePermission.view_history)
def view_version(id):
    """Show the page with the given id."""
    version = find_version(id)
    return render_page(version)


@blueprint.route('/<id>/history')
@permission_required(ContentPagePermission.view_history)
@templated
def history(id):
    page = find_page_by_id(id)
    return {
        'page': page,
    }


@blueprint.route('/create')
@permission_required(ContentPagePermission.create)
@templated
def create_form():
    """Show form to create a page."""
    form = CreateForm()
    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
@permission_required(ContentPagePermission.create)
def create():
    """Create a page."""
    form = CreateForm(request.form)

    name = form.name.data.strip()
    url_path = form.url_path.data.strip()
    if not url_path.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    page = ContentPage(
        name=name,
        party=g.party,
        url_path=url_path)
    db.session.add(page)

    version = ContentPageVersion(
        page=page,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)

    db.session.commit()

    flash_success('Die Seite "{}" wurde angelegt.', page.name)
    return redirect(url_for('.view_version', id=version.id))


@blueprint.route('/<id>/update')
@permission_required(ContentPagePermission.update)
@templated
def update_form(id):
    """Show form to update a page."""
    page = find_page_by_id(id)
    latest_version = page.get_latest_version()

    form = UpdateForm(
        obj=page,
        title=latest_version.title,
        body=latest_version.body)

    return {
        'form': form,
        'page': page,
    }


@blueprint.route('/<id>', methods=['POST'])
@permission_required(ContentPagePermission.update)
def update(id):
    """Update a page."""
    form = UpdateForm(request.form)

    page = find_page_by_id(id)

    version = ContentPageVersion(
        page=page,
        creator=g.current_user,
        title=form.title.data,
        body=form.body.data)
    db.session.add(version)
    db.session.commit()

    flash_success('Die Seite "{}" wurde aktualisiert.', page.name)
    return redirect(url_for('.view_version', id=version.id))


def find_page_by_id(id):
    return ContentPage.query.get_or_404(id)


def find_version(id):
    return ContentPageVersion.query.get_or_404(id)
