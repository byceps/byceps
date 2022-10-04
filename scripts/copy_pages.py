#!/usr/bin/env python

"""Copy a page (in its latest version) from one site to another.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.page.dbmodels import DbVersion
from byceps.services.page import page_service
from byceps.services.site.transfer.models import SiteID

from _util import call_with_app_context
from _validators import validate_site


@click.command()
@click.pass_context
@click.argument('source_site', callback=validate_site)
@click.argument('target_site', callback=validate_site)
@click.argument('page_names', nargs=-1, required=True)
def execute(ctx, source_site, target_site, page_names) -> None:
    versions = [get_version(source_site.id, name) for name in page_names]

    for version in versions:
        copy_page(target_site.id, version, ctx)

    click.secho('Done.', fg='green')


def get_version(site_id: SiteID, name: str) -> DbVersion:
    version = page_service.find_current_version_for_name(site_id, name)

    if version is None:
        raise click.BadParameter(
            f'Page "{name}" not found in site "{site_id}".'
        )

    return version


def copy_page(target_site_id: SiteID, version: DbVersion, ctx) -> None:
    page_service.create_page(
        target_site_id,
        version.page.name,
        version.page.language_code,
        version.page.url_path,
        version.creator_id,
        version.title,
        version.body,
        head=version.head,
    )

    click.secho(
        f'Copied page "{version.page.name}" to site "{target_site_id}".',
        fg='green',
    )


if __name__ == '__main__':
    call_with_app_context(execute)
