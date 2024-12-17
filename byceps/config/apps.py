"""
byceps.config.apps
~~~~~~~~~~~~~~~~~~

Models and parser for application configuration in separate
configuration file.

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError
import rtoml
import structlog

from byceps.util.result import Err, Ok, Result

from .models import AdminAppConfig, ApiAppConfig, AppsConfig, SiteAppConfig


log = structlog.get_logger()


class _BaseAppMount(BaseModel):
    server_name: str


class AdminAppMount(_BaseAppMount):
    mode: Literal['admin'] = 'admin'


class ApiAppMount(_BaseAppMount):
    mode: Literal['api'] = 'api'


class SiteAppMount(_BaseAppMount):
    mode: Literal['site'] = 'site'
    site_id: str


class AppMountsConfig(BaseModel):
    admin: AdminAppMount | None = None
    api: ApiAppMount | None = None
    sites: list[SiteAppMount] = Field(default_factory=list)


def parse_app_mounts_config(toml: str) -> Result[AppsConfig, str]:
    return (
        _parse_toml(toml)
        .and_then(_parse_app_mounts_config)
        .map(_to_apps_config)
    )


def _parse_toml(toml: str) -> Result[dict[str, Any], str]:
    try:
        return Ok(rtoml.loads(toml))
    except rtoml.TomlParsingError as e:
        return Err(str(e))


def _parse_app_mounts_config(
    data: dict[str, Any],
) -> Result[AppMountsConfig, str]:
    try:
        return Ok(AppMountsConfig.model_validate(data))
    except ValidationError as e:
        return Err(str(e))


def _to_apps_config(app_mounts_config: AppMountsConfig) -> AppsConfig:
    return AppsConfig(
        admin=_to_admin_app_config(app_mounts_config),
        api=_to_api_app_config(app_mounts_config),
        sites=_to_site_app_configs(app_mounts_config),
    )


def _to_admin_app_config(
    app_mounts_config: AppMountsConfig,
) -> AdminAppConfig | None:
    if app_mounts_config.admin:
        return AdminAppConfig(server_name=app_mounts_config.admin.server_name)
    else:
        return None


def _to_api_app_config(
    app_mounts_config: AppMountsConfig,
) -> ApiAppConfig | None:
    if app_mounts_config.api:
        return ApiAppConfig(server_name=app_mounts_config.api.server_name)
    else:
        return None


def _to_site_app_configs(
    app_mounts_config: AppMountsConfig,
) -> list[SiteAppConfig]:
    return [
        SiteAppConfig(
            server_name=site_mount.server_name, site_id=site_mount.site_id
        )
        for site_mount in app_mounts_config.sites
    ]
