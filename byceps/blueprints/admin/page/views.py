"""
byceps.blueprints.admin.page.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask import abort, g, request, url_for
from flask_babel import format_datetime, gettext

from ....services.page import page_service
from ....services.page.models import Page, PageVersion, PageVersionID
from ....services.site import site_service
from ....services.site.models import Site, SiteID
from ....services.site_navigation import site_navigation_service
from ....services.text_diff import text_diff_service
from ....services.user import user_service
from ....signals import page as page_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.iterables import pairwise
from ....util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
)

from ...site.page.templating import build_template_context

from .forms import CreateForm, SetNavMenuForm, UpdateForm


blueprint = create_blueprint('page_admin', __name__)


@blueprint.get('/for_site/<site_id>')
@permission_required('page.view')
@templated
def index_for_site(site_id):
    """List pages for that site."""
    site = _get_site(site_id)

    pages = page_service.get_pages_for_site_with_current_versions(site.id)

    user_ids = {page.current_version.creator_id for page in pages}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    return {
        'pages': pages,
        'users_by_id': users_by_id,
        'site': site,
    }


@blueprint.get('/pages/<uuid:page_id>/current_version')
@permission_required('page.view')
def view_current_version(page_id):
    """Show the current version of the page."""
    current_version_id = page_service.find_current_version_id(page_id)

    if current_version_id is None:
        abort(404)

    return view_version(current_version_id)


@blueprint.get('/versions/<uuid:version_id>')
@permission_required('page.view_history')
@templated
def view_version(version_id):
    """Show the page with the given id."""
    version = _get_version(version_id)

    page = page_service.get_page(version.page_id)
    site = site_service.get_site(page.site_id)
    creator = user_service.get_user(version.creator_id, include_avatar=True)
    is_current_version = page_service.is_current_version(page.id, version.id)

    if page.nav_menu_id:
        nav_menu = site_navigation_service.get_menu(page.nav_menu_id).unwrap()
    else:
        nav_menu = None

    return {
        'page': page,
        'site': site,
        'version': version,
        'creator': creator,
        'is_current_version': is_current_version,
        'nav_menu': nav_menu,
    }


@blueprint.get('/versions/<uuid:version_id>/preview')
@permission_required('page.view_history')
@templated
def view_version_preview(version_id):
    """Show a preview of the page version."""
    version = _get_version(version_id)

    try:
        template_context = build_template_context(
            version.title, version.head, version.body
        )

        return {
            'title': template_context['page_title'],
            'head': template_context['head'],
            'body': template_context['body'],
            'error_occurred': False,
        }
    except Exception as e:
        return {
            'error_occurred': True,
            'error_message': str(e),
        }


@blueprint.get('/pages/<uuid:page_id>/history')
@permission_required('page.view_history')
@templated
def history(page_id):
    """Show index of page versions."""
    page = _get_page(page_id)

    versions = page_service.get_versions(page.id)
    versions_pairwise = list(pairwise(versions + [None]))

    user_ids = {version.creator_id for version in versions}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    site = site_service.get_site(page.site_id)

    return {
        'page': page,
        'versions_pairwise': versions_pairwise,
        'users_by_id': users_by_id,
        'site': site,
    }


@blueprint.get(
    '/versions/<uuid:from_version_id>/compare_to/<uuid:to_version_id>'
)
@permission_required('page.view_history')
@templated
def compare_versions(from_version_id, to_version_id):
    """Show the difference between two versions."""
    from_version = _get_version(from_version_id)
    to_version = _get_version(to_version_id)

    if from_version.page_id != to_version.page_id:
        abort(400, 'The versions do not belong to the same page.')

    html_diff_title = _create_html_diff(from_version, to_version, 'title')
    html_diff_head = _create_html_diff(from_version, to_version, 'head')
    html_diff_body = _create_html_diff(from_version, to_version, 'body')

    page = page_service.get_page(from_version.page_id)
    site = site_service.get_site(page.site_id)

    return {
        'page': page,
        'diff_title': html_diff_title,
        'diff_head': html_diff_head,
        'diff_body': html_diff_body,
        'site': site,
    }


def _create_html_diff(
    from_version: PageVersion,
    to_version: PageVersion,
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


@blueprint.get('/for_site/<site_id>/create')
@permission_required('page.create')
@templated
def create_form(site_id, erroneous_form=None):
    """Show form to create a page."""
    site = _get_site(site_id)

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_language_code_choices()

    return {
        'form': form,
        'site': site,
    }


@blueprint.post('/for_site/<site_id>')
@permission_required('page.create')
def create(site_id):
    """Create a page."""
    site = _get_site(site_id)

    form = CreateForm(request.form)
    form.set_language_code_choices()

    if not form.validate():
        return create_form(site.id, form)

    name = form.name.data.strip().lower()
    language_code = form.language_code.data
    url_path = form.url_path.data.strip()
    creator = g.user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()

    version, event = page_service.create_page(
        site.id,
        name,
        language_code,
        url_path,
        creator.id,
        title,
        body,
        head=head,
    )

    flash_success(gettext('Page has been created.'))

    page_signals.page_created.send(None, event=event)

    return redirect_to('.view_version', version_id=version.id)


@blueprint.get('/pages/<uuid:page_id>/update')
@permission_required('page.update')
@templated
def update_form(page_id, erroneous_form=None):
    """Show form to update a page."""
    page = _get_page(page_id)

    current_version_id = page_service.find_current_version_id(page.id)
    page_aggregate = page_service.find_page_aggregate(current_version_id)

    form = erroneous_form if erroneous_form else UpdateForm(obj=page_aggregate)
    form.set_language_code_choices()

    site = site_service.get_site(page.site_id)

    return {
        'form': form,
        'page': page,
        'site': site,
    }


@blueprint.post('/pages/<uuid:page_id>')
@permission_required('page.update')
def update(page_id):
    """Update a page."""
    page = _get_page(page_id)

    form = UpdateForm(request.form)
    form.set_language_code_choices()

    if not form.validate():
        return update_form(page.id, form)

    language_code = form.language_code.data
    url_path = form.url_path.data.strip()
    creator = g.user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()

    version, event = page_service.update_page(
        page.id,
        language_code,
        url_path,
        creator.id,
        title,
        head,
        body,
    )

    flash_success(gettext('Page has been updated.'))

    page_signals.page_updated.send(None, event=event)

    return redirect_to('.view_version', version_id=version.id)


@blueprint.delete('/pages/<uuid:page_id>')
@permission_required('page.delete')
@respond_no_content_with_location
def delete(page_id):
    """Delete a page."""
    page = _get_page(page_id)

    page_name = page.name
    site_id = page.site_id

    success, event = page_service.delete_page(page.id, initiator_id=g.user.id)

    if not success:
        flash_error(
            gettext('Page "%(name)s" could not be deleted.', name=page_name)
        )
        return url_for('.view_current_version', page_id=page.id)

    flash_success(gettext('Page "%(name)s" has been deleted.', name=page_name))

    page_signals.page_deleted.send(None, event=event)

    return url_for('.index_for_site', site_id=site_id)


@blueprint.get('/pages/<uuid:page_id>/set_nav_menu')
@permission_required('page.update')
@templated
def set_nav_menu_form(page_id, erroneous_form=None):
    """Show form to set navigation menu for a page."""
    page = _get_page(page_id)

    site = site_service.get_site(page.site_id)

    form = erroneous_form if erroneous_form else SetNavMenuForm(obj=page)
    form.set_nav_menu_choices(site.id)

    return {
        'form': form,
        'page': page,
        'site': site,
    }


@blueprint.post('/pages/<uuid:page_id>/set_nav_menu')
@permission_required('page.update')
def set_nav_menu(page_id):
    """Set navigation menu for a page."""
    page = _get_page(page_id)

    site = site_service.get_site(page.site_id)

    form = SetNavMenuForm(request.form)
    form.set_nav_menu_choices(site.id)

    if not form.validate():
        return set_nav_menu_form(page.id, form)

    nav_menu_id = form.nav_menu_id.data or None

    page_service.set_nav_menu_id(page.id, nav_menu_id)

    flash_success(gettext('Page has been updated.'))

    return redirect_to('.view_current_version', page_id=page.id)


def _get_site(site_id) -> Site:
    site = site_service.find_site(SiteID(site_id))

    if site is None:
        abort(404)

    return site


def _get_page(page_id) -> Page:
    page = page_service.find_page(page_id)

    if page is None:
        abort(404)

    return page


def _get_version(version_id: PageVersionID) -> PageVersion:
    version = page_service.find_version(version_id)

    if version is None:
        abort(404)

    return version
