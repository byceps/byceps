"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.app_dispatcher import parse_apps_config
from byceps.config.models import (
    AdminAppConfig,
    ApiAppConfig,
    AppsConfig,
    SiteAppConfig,
)
from byceps.util.result import Err, Ok


def test_parse_apps_config_with_empty_input():
    expected = Ok(
        AppsConfig(
            admin=None,
            api=None,
            sites=[],
        )
    )

    toml = ''

    assert parse_apps_config(toml) == expected


def test_parse_apps_config_with_modespecific_sections():
    expected = Ok(
        AppsConfig(
            admin=AdminAppConfig(server_name='admin.byceps.test'),
            api=ApiAppConfig(server_name='api.byceps.test'),
            sites=[
                SiteAppConfig(
                    server_name='www.byceps.test', site_id='internet'
                ),
                SiteAppConfig(
                    server_name='local.byceps.test', site_id='intranet'
                ),
            ],
        )
    )

    toml = """
    [admin]
    server_name = "admin.byceps.test"

    [api]
    server_name = "api.byceps.test"

    [[sites]]
    server_name = "www.byceps.test"
    site_id = "internet"

    [[sites]]
    server_name = "local.byceps.test"
    site_id = "intranet"
    """

    assert parse_apps_config(toml) == expected


def test_parse_apps_config_with_conflicting_server_names():
    toml = """
    [[sites]]
    server_name = "www.byceps.test"
    site_id = "one"

    [[sites]]
    server_name = "www.byceps.test"
    site_id = "two"
    """

    assert parse_apps_config(toml) == Err(
        'Non-unique server names configured: www.byceps.test'
    )
