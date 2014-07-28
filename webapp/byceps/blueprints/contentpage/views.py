# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import sys
import warnings

from flask import abort, g, redirect, render_template, request, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success, \
    get_blueprint_views_module
from ...util.templating import templated

from .forms import CreateForm, UpdateForm
from .models import ContentPage


blueprint = create_blueprint('contentpage', __name__)


@blueprint.route('/')
@templated
def index():
    """List pages."""
    pages = ContentPage.query.all()
    return {'pages': pages}


def add_routes_for_pages(app):
    """Register routes for pages with the application."""
    blueprint_name = 'contentpage'
    pages = ContentPage.query.all()
    for page in pages:
        endpoint = '{}.{}'.format(blueprint_name, page.name)
        view_func = view_latest_by_name
        defaults = {'name': page.name}
        app.add_url_rule(page.url, endpoint, view_func, defaults=defaults)


def view_latest_by_name(name):
    """Show the latest version of the page with the given name."""
    try:
        template = _create_env(load_func=_load_template_by_name).get_template(name)
        title, current_page = _extract_metadata(name, template)
        body = template.render()
        context = {
            'title': title,
            'current_page': current_page,
            'body': body,
        }
        return render_template('contentpage/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in content page markup:', e, file=sys.stderr)
        context = {
            'message': str(e),
        }
        return render_template('contentpage/error.html', **context), 500


@blueprint.route('/versions/<id>')
def view_version(id):
    """Show the page with the given id."""
    try:
        template = _create_env(load_func=_load_template_by_version).get_template(id)
        title, current_page = _extract_metadata(id, template)
        body = template.render()
        context = {
            'title': title,
            'current_page': current_page,
            'body': body,
        }
        return render_template('contentpage/view.html', **context)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        print('Error in content page markup:', e, file=sys.stderr)
        context = {
            'message': str(e),
        }
        return render_template('contentpage/error.html', **context), 500


def _create_env(load_func):
    loader = FunctionLoader(load_func)
    env = ImmutableSandboxedEnvironment(
        loader=loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['url_for'] = url_for

    return env


def _load_template_by_name(name):
    page = ContentPage.query \
        .filter_by(name=name) \
        .order_by(ContentPage.created_at.desc()) \
        .first()

    if page is not None:
        return page.body


def _load_template_by_version(id):
    page = ContentPage.query.get(id)

    if page is not None:
        return page.body


def _extract_metadata(id, template):
    try:
        title = template.module.title
        current_page = template.module.current_page
    except AttributeError:
        warnings.warn(
            'No title and/or current page set for page "{}".'.format(id))
        title = ''
        current_page = None
    return title, current_page


@blueprint.route('/<name>/history')
@templated
def history(name):
    versions = ContentPage.query \
        .filter_by(name=name) \
        .order_by(ContentPage.created_at.desc()) \
        .all()
    if not versions:
        abort(404)

    page = versions[0]
    return {
        'name': page.name,
        'url': page.url,
        'versions': versions,
    }


@blueprint.route('/create')
@templated
def create_form():
    """Show form to create a page."""
    form = CreateForm()
    return {
        'form': form,
    }


@blueprint.route('/', methods=['POST'])
def create():
    """Create a page."""
    form = CreateForm(request.form)

    page = ContentPage(
        creator=g.current_user,
        name=form.name.data,
        url=form.url.data,
        body=form.body.data)
    db.session.add(page)
    db.session.commit()

    flash_success('Die Seite "{}" wurden angelegt.', page.name)
    return redirect(url_for('.index'))


@blueprint.route('/<name>/update')
@templated
def update_form(name):
    """Show form to update a page."""
    page = find_page_by_name(name)
    form = UpdateForm(obj=page)
    return {
        'form': form,
        'page': page,
    }


@blueprint.route('/<name>', methods=['POST'])
def update(name):
    """Update a page."""
    form = UpdateForm(request.form)

    original_page = find_page_by_name(name)

    page = ContentPage(
        creator=g.current_user,
        name=original_page.name,
        url=original_page.url,
        body=form.body.data)
    db.session.add(page)
    db.session.commit()

    flash_success('Die Seite "{}" wurde aktualisiert.', page.name)
    return redirect(url_for('.view_version', id=page.id))


def find_page_by_name(name):
    return ContentPage.query.filter_by(name=name).first_or_404()
