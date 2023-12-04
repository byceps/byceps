#!/usr/bin/env python

"""Copy a page (in its latest version) from one site to another.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.page import page_service
from byceps.services.page.errors import (
    PageAlreadyExistsError,
    PageNotFoundError,
)
from byceps.services.site.models import Site
from byceps.util.result import Err, Ok

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
    match page_service.copy_page(source_site, target_site, name, language_code):
        case Ok(_):
            click.secho(
                f'Copied page "{name}" ({language_code}) from site "{source_site.id}" to site "{target_site.id}".',
                fg='green',
            )
        case Err(PageNotFoundError()):
            click.secho(
                f'Page "{name}" ({language_code}) not found in site "{source_site.id}".',
                fg='red',
            )
        case Err(PageAlreadyExistsError()):
            click.secho(
                f'Page "{name}" ({language_code}) already exists in site "{target_site.id}".',
                fg='red',
            )


if __name__ == '__main__':
    call_with_app_context(execute)
