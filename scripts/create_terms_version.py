#!/usr/bin/env python

"""Create a new terms of service version.

However, do not set the new version as the current version for the brand.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.consent import subject_service as consent_subject_service
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import SnippetVersionID
from byceps.services.terms import document_service as terms_document_service
from byceps.services.terms.transfer.models import DocumentID
from byceps.services.terms import version_service as terms_version_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_brand


def validate_document_id(ctx, param, value) -> DocumentID:
    document = terms_document_service.find_document(value)

    if not document:
        raise click.BadParameter(f'Unknown document ID "{value}".')

    return document.id


def validate_snippet_version_id(ctx, param, value) -> SnippetVersionID:
    snippet_version = snippet_service.find_snippet_version(value)

    if not snippet_version:
        raise click.BadParameter(f'Unknown snippet_version ID "{value}".')

    return snippet_version.id


@click.command()
@click.argument('brand', callback=validate_brand)
@click.argument('document_id', callback=validate_document_id)
@click.argument('title')
@click.argument('snippet_version_id', callback=validate_snippet_version_id)
@click.argument('consent_subject_name_suffix')
def execute(
    brand, document_id, title, snippet_version_id, consent_subject_name_suffix
):
    consent_subject = _create_consent_subject(
        brand, title, consent_subject_name_suffix
    )

    terms_version_service.create_version(
        document_id, title, snippet_version_id, consent_subject.id
    )

    click.secho('Done.', fg='green')


def _create_consent_subject(brand, title, consent_subject_name_suffix):
    subject_name = f'{brand.id}_terms-of-service_{consent_subject_name_suffix}'
    subject_title = f'AGB {brand.title} / {title}'
    checkbox_label = 'Ich akzeptiere die <a href="{url}" target="_blank">Allgemeinen Geschäftsbedingungen</a>'
    checkbox_link_target = '/terms/'

    return consent_subject_service.create_subject(
        subject_name, subject_title, checkbox_label, checkbox_link_target
    )


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
