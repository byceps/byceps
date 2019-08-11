#!/usr/bin/env python

"""Set the current version of the terms of service for a brand.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, List, Optional

import click
from pick import pick

from byceps.services.terms.models.version import Version
from byceps.services.terms.transfer.models import VersionID
from byceps.services.terms import version_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_brand


@click.command()
@click.argument('brand', callback=validate_brand)
def execute(brand):
    versions = version_service.get_versions_for_brand(brand.id)
    current_version_id = version_service.find_current_version_id(brand.id)

    versions_by_id = {v.id: v for v in versions}

    # Ask user which version to set as the current one.
    selected_version_id = _request_version_id(versions_by_id,
                                              current_version_id)

    # Set current version.
    version_service.set_current_version(brand.id, selected_version_id)

    # Confirm update to user.
    selected_version_title = versions_by_id[selected_version_id].title
    click.secho(
        f'Current version for brand ID "{brand.id}" '
        f'was set to "{selected_version_title}".',
        fg='green')


def _request_version_id(versions_by_id: Dict[VersionID, Version],
                        current_version_id: Optional[VersionID]
                       ) -> VersionID:
    version_ids = _get_version_ids_latest_first(versions_by_id)

    if not version_ids:
        raise click.BadParameter(
            'No versions for brand available to choose from.')

    def get_option_title(version_id):
        version = versions_by_id[version_id]
        created_at_str = version.created_at.strftime('%Y-%m-%d %H:%M:%S')

        return f'"{version.title}"\t\t{created_at_str}'

    if current_version_id is not None:
        current_version_option_index = version_ids.index(current_version_id)
    else:
        current_version_option_index = 0

    selection = pick(
        version_ids,
        title='Choose version to set as the current one:',
        options_map_func=get_option_title,
        default_index=current_version_option_index)

    return selection[0]


def _get_version_ids_latest_first(versions_by_id: Dict[VersionID, Version]
                                 ) -> List[VersionID]:
    versions = versions_by_id.values()

    versions_latest_first = list(sorted(versions,
                                        key=lambda v: v.created_at,
                                        reverse=True))

    return [v.id for v in versions_latest_first]


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
