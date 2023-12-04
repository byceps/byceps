#!/usr/bin/env python

"""Copy a page (in its latest version) from one site to another.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.page import page_service
from byceps.services.site.models import Site
from byceps.services.user import user_service

from _util import call_with_app_context
from _validators import validate_site


@click.command()
@click.pass_context
@click.argument('source_site', callback=validate_site)
@click.argument('target_site', callback=validate_site)
@click.argument('language_code')
@click.argument('page_names', nargs=-1, required=True)
def execute(
    ctx, source_site, target_site, language_code: str, page_names
) -> None:
    for name in page_names:
        copy_page(source_site, target_site, name, language_code, ctx)

    click.secho('Done.', fg='green')


def copy_page(
    source_site: Site, target_site: Site, name: str, language_code: str, ctx
) -> None:
    version = page_service.find_current_version_for_name(
        source_site.id, name, language_code
    )
    if version is None:
        click.secho(
            f'Page "{name}" ({language_code}) not found in site "{source_site.id}".',
            fg='red',
        )
        return None

    creator = user_service.get_user(version.creator_id)

    page_service.create_page(
        target_site,
        version.page.name,
        version.page.language_code,
        version.page.url_path,
        creator,
        version.title,
        version.body,
        head=version.head,
    )

    click.secho(
        f'Copied page "{version.page.name}" ({language_code}) to site "{target_site.id}".',
        fg='green',
    )


if __name__ == '__main__':
    call_with_app_context(execute)
