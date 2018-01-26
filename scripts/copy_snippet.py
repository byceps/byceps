#!/usr/bin/env python

"""Copy a snippet (in its latest version) from one party to another.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.snippet.models.snippet import SnippetType
from byceps.services.snippet import service as snippet_service
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context
from bootstrap.validators import validate_party


@click.command()
@click.pass_context
@click.argument('source_party', callback=validate_party)
@click.argument('target_party', callback=validate_party)
@click.argument('snippet_name')
def execute(ctx, source_party, target_party, snippet_name):
    snippet_version = snippet_service \
        .find_current_version_of_snippet_with_name(
            source_party.id, snippet_name)

    if snippet_version is None:
        raise click.BadParameter('Unknown snippet name "{}" for party "{}".'
            .format(snippet_name, source_party.id))

    snippet = snippet_version.snippet

    if snippet.type_ == SnippetType.document:
        snippet_service.create_document(
            target_party.id,
            snippet.name,
            snippet_version.creator_id,
            snippet_version.title,
            snippet_version.body,
            head=snippet_version.head,
            image_url_path=snippet_version.image_url_path
        )
    elif snippet.type_ == SnippetType.fragment:
        snippet_service.create_fragment(
            target_party.id,
            snippet.name,
            snippet_version.creator_id,
            snippet_version.body
        )
    else:
        ctx.fail("Unknown snippet type '{}'.".format(snippet.type_))

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
