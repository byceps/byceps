#!/usr/bin/env python

"""Export all permissions, roles, and their relations as TOML to STDOUT.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.authorization import impex_service

from _util import app_context


@click.command()
def execute():
    print(impex_service.export())


if __name__ == '__main__':
    with app_context():
        execute()
