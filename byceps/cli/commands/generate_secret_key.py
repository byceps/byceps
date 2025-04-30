"""
byceps.cli.command.generate_secret_key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate a secure secret key.

Suitable as a value for ``secret_key`` in a BYCEPS configuration file.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import secrets

import click


@click.command()
def generate_secret_key() -> None:
    """Generate a secure secret key."""
    click.echo(secrets.token_hex())
