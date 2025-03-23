"""
byceps.util.framework.blueprint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint utilities

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from importlib import import_module
from types import ModuleType

from flask import Blueprint, Flask


BlueprintReg = tuple[str, str | None]


def create_blueprint(name: str, import_name: str) -> Blueprint:
    """Create a blueprint with default folder names."""
    return Blueprint(
        name, import_name, static_folder='static', template_folder='templates'
    )


def get_blueprint(package_path: str) -> Blueprint:
    """Load the blueprint from the named module.

    The module is expected to be located inside the ``blueprints``
    sub-package and to contain a blueprint instance named ``blueprint``.
    """
    module = _get_blueprint_views_module(package_path)
    return module.blueprint


def _get_blueprint_views_module(package_path: str) -> ModuleType:
    """Import and return the 'views' module located in the specified
    blueprint package.
    """
    return import_module(f'byceps.blueprints.{package_path}.views')


def register_blueprints(
    app: Flask | Blueprint, blueprints: Iterable[BlueprintReg]
) -> None:
    """Register blueprints on the application."""
    for package_path, url_prefix in blueprints:
        blueprint = get_blueprint(package_path)
        app.register_blueprint(blueprint, url_prefix=url_prefix)
