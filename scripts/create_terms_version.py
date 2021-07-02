#!/usr/bin/env python

"""Create a new terms of service version.

However, do not set the new version as the current version for the brand.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.consent import subject_service as consent_subject_service

from _util import call_with_app_context
from _validators import validate_brand


@click.command()
@click.argument('brand', callback=validate_brand)
@click.argument('title')
@click.argument('consent_subject_name_suffix')
def execute(brand, title, consent_subject_name_suffix):
    consent_subject = _create_consent_subject(
        brand, title, consent_subject_name_suffix
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
    call_with_app_context(execute)
