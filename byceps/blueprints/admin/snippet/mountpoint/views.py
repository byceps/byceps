"""
byceps.blueprints.admin.snippet.mountpoint.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional
from flask import abort, request
from flask_babel import gettext

from .....services.brand.transfer.models import Brand
from .....services.site import service as site_service
from .....services.site.transfer.models import Site
from .....services.snippet import mountpoint_service, service as snippet_service
from .....services.snippet.transfer.models import Scope
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to, respond_no_content

from ..helpers import (
    find_brand_for_scope,
    find_site_by_id,
    find_site_for_scope,
    find_snippet_by_id,
)

from .forms import CreateForm, SiteSelectForm


blueprint = create_blueprint('snippet_mountpoint_admin', __name__)


@blueprint.get('/for_site/<site_id>')
@permission_required('snippet.view')
@templated
def index(site_id):
    """List mountpoints for that site."""
    scope = Scope.for_site(site_id)

    mountpoints = mountpoint_service.get_mountpoints_for_site(site_id)

    snippet_ids = {mp.snippet_id for mp in mountpoints}
    snippets = snippet_service.get_snippets(snippet_ids)
    snippets_by_snippet_id = {snippet.id: snippet for snippet in snippets}

    mountpoints_and_snippets = [
        (mp, snippets_by_snippet_id[mp.snippet_id]) for mp in mountpoints
    ]

    site = find_site_for_scope(scope)

    return {
        'scope': scope,
        'mountpoints_and_snippets': mountpoints_and_snippets,
        'site': site,
    }


@blueprint.get('/for_snippet/<uuid:snippet_id>/select_site')
@permission_required('snippet_mountpoint.create')
@templated
def site_select_form(snippet_id, *, erroneous_form=None):
    """Show form to select a site to create a mountpoint for."""
    snippet = find_snippet_by_id(snippet_id)

    scope = snippet.scope

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    sites = _get_sites_to_potentially_mount_to(brand, site)

    form = erroneous_form if erroneous_form else SiteSelectForm()
    form.set_site_id_choices(sites)

    return {
        'scope': scope,
        'snippet': snippet,
        'form': form,
        'brand': brand,
        'site': site,
    }


@blueprint.post('/for_snippet/<uuid:snippet_id>/select_site')
@permission_required('snippet_mountpoint.create')
def site_select(snippet_id):
    """Redirect to form to create a mountpoint."""
    snippet = find_snippet_by_id(snippet_id)

    scope = snippet.scope

    brand = find_brand_for_scope(scope)
    site = find_site_for_scope(scope)

    sites = _get_sites_to_potentially_mount_to(brand, site)

    form = SiteSelectForm(request.form)
    form.set_site_id_choices(sites)

    if not form.validate():
        return site_select_form(snippet.id, erroneous_form=form)

    site_id = form.site_id.data

    return redirect_to('.create_form', snippet_id=snippet.id, site_id=site_id)


def _get_sites_to_potentially_mount_to(
    brand: Optional[Brand] = None, site: Optional[Site] = None
) -> set[Site]:
    if site is not None:
        return {site}
    elif brand is not None:
        return site_service.get_sites_for_brand(brand.id)
    else:
        return site_service.get_all_sites()


@blueprint.get('/for_snippet/<uuid:snippet_id>/for_site/<site_id>/create')
@permission_required('snippet_mountpoint.create')
@templated
def create_form(snippet_id, site_id, *, erroneous_form=None):
    """Show form to create a mountpoint."""
    snippet = find_snippet_by_id(snippet_id)
    site = find_site_by_id(site_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'snippet': snippet,
        'form': form,
        'site': site,
    }


@blueprint.post('/for_snippet/<uuid:snippet_id>/for_site/<site_id>')
@permission_required('snippet_mountpoint.create')
def create(snippet_id, site_id):
    """Create a mountpoint."""
    snippet = find_snippet_by_id(snippet_id)
    site = find_site_by_id(site_id)

    form = CreateForm(request.form)

    if not form.validate():
        return create_form(snippet.id, site.id, erroneous_form=form)

    endpoint_suffix = form.endpoint_suffix.data.strip()
    url_path = form.url_path.data.strip()

    mountpoint = mountpoint_service.create_mountpoint(
        site.id, endpoint_suffix, url_path, snippet.id
    )

    flash_success(
        gettext(
            'Mountpoint for "%(url_path)s" has been created.',
            url_path=mountpoint.url_path,
        )
    )

    return redirect_to('.index', site_id=site.id)


@blueprint.delete('/mountpoints/<uuid:mountpoint_id>')
@permission_required('snippet_mountpoint.delete')
@respond_no_content
def delete(mountpoint_id):
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
