"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.app_dispatcher import (
    AdminAppMount,
    ApiAppMount,
    AppsConfig,
    SiteAppMount,
    parse_apps_config,
)
from byceps.util.result import Err, Ok


def test_parse_apps_config_with_empty_input():
    expected = Ok(AppsConfig())

    toml = ''

    assert parse_apps_config(toml) == expected


def test_parse_apps_config_with_modespecific_sections():
    expected = Ok(
        AppsConfig(
            admin=AdminAppMount(server_name='admin.byceps.test'),
            api=ApiAppMount(server_name='api.byceps.test'),
            sites=[
                SiteAppMount(server_name='www.byceps.test', site_id='internet'),
                SiteAppMount(
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


def test_parse_apps_config_with_app_mounts():
    expected = Ok(
        AppsConfig(
            app_mounts=[
                AdminAppMount(server_name='admin.byceps.test'),
                ApiAppMount(server_name='api.byceps.test'),
                SiteAppMount(server_name='www.byceps.test', site_id='internet'),
                SiteAppMount(
                    server_name='local.byceps.test', site_id='intranet'
                ),
            ]
        )
    )

    toml = """
    [[app_mounts]]
    server_name = "admin.byceps.test"
    mode = "admin"

    [[app_mounts]]
    server_name = "api.byceps.test"
    mode = "api"

    [[app_mounts]]
    server_name = "www.byceps.test"
    mode = "site"
    site_id = "internet"

    [[app_mounts]]
    server_name = "local.byceps.test"
    mode = "site"
    site_id = "intranet"
    """

    assert parse_apps_config(toml) == expected


def test_parse_apps_config_with_conflicting_server_names_in_app_mounts():
    toml = """
    [[app_mounts]]
    server_name = "www.byceps.test"
    mode = "site"
    site_id = "one"

    [[app_mounts]]
    server_name = "www.byceps.test"
    mode = "site"
    site_id = "two"
    """

    assert parse_apps_config(toml) == Err(
        'Non-unique server names configured: www.byceps.test'
    )


def test_parse_apps_config_with_conflicting_server_names():
    toml = """
    [[sites]]
    server_name = "www.byceps.test"
    site_id = "one"

    [[app_mounts]]
    server_name = "www.byceps.test"
    mode = "site"
    site_id = "two"
    """

    assert parse_apps_config(toml) == Err(
        'Non-unique server names configured: www.byceps.test'
    )
