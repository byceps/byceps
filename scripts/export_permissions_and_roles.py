#!/usr/bin/env python

"""Export all permissions, roles, and their relations as TOML to STDOUT.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.authorization import impex_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
def execute():
    print(impex_service.export())


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
