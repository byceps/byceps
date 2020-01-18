"""
byceps.util.templating
~~~~~~~~~~~~~~~~~~~~~~

Templating utilities

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from typing import Any, Dict, Optional, Set

from jinja2 import (
    BaseLoader,
    Environment,
    FileSystemLoader,
    FunctionLoader,
    Template,
    TemplateNotFound,
)
from jinja2.sandbox import ImmutableSandboxedEnvironment


def load_template(source: str, *, template_globals: Dict[str, Any] = None):
    """Load a template from source, using the sandboxed environment."""
    env = create_sandboxed_environment()

    if template_globals is not None:
        env.globals.update(template_globals)

    return env.from_string(source)


def create_sandboxed_environment(
    *, loader: Optional[BaseLoader] = None, autoescape: bool = True
) -> Environment:
    """Create a sandboxed environment."""
    if loader is None:
        # A loader that never finds a template.
        loader = FunctionLoader(lambda name: None)

    return ImmutableSandboxedEnvironment(loader=loader, autoescape=autoescape)


def get_variable_value(template: Template, name: str) -> Optional[Any]:
    """Return the named variable's value from the template, or `None` if
    the variable is not defined.
    """
    try:
        return getattr(template.module, name)
    except AttributeError:
        return None


class SiteTemplateOverridesLoader(BaseLoader):
    """Look for site-specific template overrides."""

    def __init__(self) -> None:
        self._loaders_by_site_id = {}

    def get_source(self, environment: Environment, template: Template) -> str:
        loader = self._get_loader()

        try:
            return loader.get_source(environment, template)
        except TemplateNotFound:
            pass

        # Site does not override template.
        raise TemplateNotFound(template)

    def _get_loader(self) -> BaseLoader:
        """Look up site-specific loader.

        Create if not available.
        """
        site_id = g.site_id

        loader = self._loaders_by_site_id.get(site_id)

        if loader is None:
            loader = self._create_loader(site_id)
            self._loaders_by_site_id[site_id] = loader

        return loader

    def _create_loader(self, site_id: str) -> BaseLoader:
        """Create file system loader for site-specific search path."""
        search_path = f'sites/{site_id}/template_overrides'
        return FileSystemLoader(search_path)
