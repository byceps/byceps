#!/usr/bin/env python

"""Copy a snippet (in its latest version) from one site to another.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope, SnippetType
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_site


@click.command()
@click.pass_context
@click.argument('source_site', callback=validate_site)
@click.argument('target_site', callback=validate_site)
@click.argument('snippet_name')
def execute(ctx, source_site, target_site, snippet_name):
    source_scope = Scope.for_site(source_site.id)
    target_scope = Scope.for_site(target_site.id)

    snippet_version = snippet_service.find_current_version_of_snippet_with_name(
        source_scope, snippet_name
    )

    if snippet_version is None:
        raise click.BadParameter(
            f'Unknown snippet name "{snippet_name}" '
            f'for site "{source_site.id}".'
        )

    snippet = snippet_version.snippet

    if snippet.type_ == SnippetType.document:
        snippet_service.create_document(
            target_scope,
            snippet.name,
            snippet_version.creator_id,
            snippet_version.title,
            snippet_version.body,
            head=snippet_version.head,
            image_url_path=snippet_version.image_url_path,
        )
    elif snippet.type_ == SnippetType.fragment:
        snippet_service.create_fragment(
            target_scope,
            snippet.name,
            snippet_version.creator_id,
            snippet_version.body,
        )
    else:
        ctx.fail(f"Unknown snippet type '{snippet.type_}'.")

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
