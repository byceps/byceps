# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import sys
import warnings

from flask import abort, redirect, render_template, request, url_for
from jinja2 import FunctionLoader, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment
from werkzeug.routing import BuildError

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated

from .forms import UpdateForm
from .models import collect_all_content_page_ids, ContentPage, \
    ContentPageReference


blueprint = create_blueprint('contentpage', __name__)


@blueprint.route('/')
@templated
def index():
    """List users."""
    ids = collect_all_content_page_ids()
    references = list(generate_references(ids))
    return {'references': references}


def generate_references(ids):
    for id in ids:
        view_url = generate_view_url_for(id)
        update_url = url_for('.update_form', id=id)
        yield ContentPageReference(id, view_url, update_url)


def generate_view_url_for(id):
    try:
        return url_for(id)
    except BuildError:
        return None


@blueprint.route('/<id>')
def view(id):
    """Show the page."""
    try:
        template = _create_env().get_template(id)
        title, current_page = _extract_metadata(template)
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
            'message': e.message,
        }
        return render_template('contentpage/error.html', **context), 500


def _create_env():
    env = ImmutableSandboxedEnvironment(
        loader=_loader,
        autoescape=True,
        trim_blocks=True)

    env.globals['url_for'] = url_for

    return env


def _load_template(name):
    content_page = _fetch_latest_content_page(name)
    if content_page is None:
        return None
    return content_page.body


_loader = FunctionLoader(_load_template)


def _fetch_latest_content_page(id):
    return ContentPage.query \
        .filter_by(id=id) \
        .order_by(ContentPage.created_at.desc()) \
        .first()


def _extract_metadata(template):
    try:
        title = template.module.title
        current_page = template.module.current_page
    except AttributeError:
        warnings.warn(
            'No title and/or current page set for page "{}".'.format(id))
        title = ''
        current_page = None
    return title, current_page


@blueprint.route('/<id>/update')
@templated
def update_form(id):
    """Show form to update a content page."""
    page = find_page(id)
    form = UpdateForm(obj=page)
    return {
        'form': form,
        'page': page,
    }


@blueprint.route('/<id>', methods=['POST'])
def update(id):
    """Update a content page."""
    page = find_page(id)

    form = UpdateForm(request.form)
    page.body = form.body.data
    db.session.commit()

    flash_success('Die Änderungen wurden übernommen.')
    return redirect(url_for(id))


def find_page(id):
    return ContentPage.query.filter_by(id=id).first_or_404()
