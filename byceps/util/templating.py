"""
byceps.util.templating
~~~~~~~~~~~~~~~~~~~~~~

Templating utilities

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from flask import g
from jinja2 import (
    BaseLoader,
    Environment,
    FileSystemLoader,
    FunctionLoader,
    Template,
    TemplateNotFound,
)
from jinja2.sandbox import ImmutableSandboxedEnvironment


SITES_PATH = Path('sites')


def load_template(
    source: str, *, template_globals: dict[str, Any] | None = None
) -> Template:
    """Load a template from source, using the sandboxed environment."""
    env = create_sandboxed_environment()

    if template_globals is not None:
        env.globals.update(template_globals)

    return env.from_string(source)


def create_sandboxed_environment(
    *, loader: BaseLoader | None = None, autoescape: bool = True
) -> Environment:
    """Create a sandboxed environment."""
    if loader is None:
        # A loader that never finds a template.
        loader = FunctionLoader(lambda name: None)

    return ImmutableSandboxedEnvironment(loader=loader, autoescape=autoescape)


class SiteTemplateOverridesLoader(BaseLoader):
    """Look for site-specific template overrides."""

    def __init__(self) -> None:
        self._loaders_by_site_id: dict[str, BaseLoader] = {}

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        site = getattr(g, 'site', None)
        if not site:
            # Site could not be determined. Thus, no site-specific
            # template loader is available.
            raise TemplateNotFound(template)

        loader = self._get_loader(site.id)

        try:
            return loader.get_source(environment, template)
        except TemplateNotFound:
            pass

        # Site does not override template.
        raise TemplateNotFound(template)

    def _get_loader(self, site_id: str) -> BaseLoader:
        """Look up site-specific loader.

        Create if not available.
        """
        loader = self._loaders_by_site_id.get(site_id)

        if loader is None:
            loader = self._create_loader(site_id)
            self._loaders_by_site_id[site_id] = loader

        return loader

    def _create_loader(self, site_id: str) -> BaseLoader:
        """Create file system loader for site-specific search path."""
        search_path = SITES_PATH / site_id / 'template_overrides'
        return FileSystemLoader(search_path)


def create_site_template_loader() -> BaseLoader:
    return SiteTemplateOverridesLoader()
