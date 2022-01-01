"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

from byceps.events.user import UserDetailsUpdated
from byceps.services.user import (
    command_service as user_command_service,
    log_service,
    service as user_service,
)


def test_update_user_address(site_app, make_user):
    old_first_names = 'Rainer'
    old_last_name = 'Zufall'
    old_date_of_birth = None
    old_country = 'Germany'
    old_zip_code = '22999'
    old_city = 'Büttenwarder'
    old_street = 'Dorfweg 23'
    old_phone_number = None

    new_first_names = 'Rainer'
    new_last_name = 'Zufall'
    new_date_of_birth = None
    new_country = 'Germany'
    new_zip_code = '20099'
    new_city = 'Hamburg'
    new_street = 'Kirchenallee 1'
    new_phone_number = None

    user = make_user(
        first_names=old_first_names,
        last_name=old_last_name,
        date_of_birth=old_date_of_birth,
        country=old_country,
        zip_code=old_zip_code,
        city=old_city,
        street=old_street,
        phone_number=old_phone_number,
    )

    log_entries_before = log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 1  # user creation

    # -------------------------------- #

    event = user_command_service.update_user_details(
        user.id,
        new_first_names,
        new_last_name,
        new_date_of_birth,
        new_country,
        new_zip_code,
        new_city,
        new_street,
        new_phone_number,
        user.id,
    )

    # -------------------------------- #

    assert isinstance(event, UserDetailsUpdated)
    assert event.initiator_id == user.id
    assert event.initiator_screen_name == user.screen_name
    assert event.user_id == user.id
    assert event.user_screen_name == user.screen_name

    user_after = user_command_service._get_user(user.id)
    assert user_after.detail.first_names == new_first_names
    assert user_after.detail.last_name == new_last_name
    assert user_after.detail.date_of_birth == new_date_of_birth
    assert user_after.detail.country == new_country
    assert user_after.detail.zip_code == new_zip_code
    assert user_after.detail.city == new_city
    assert user_after.detail.street == new_street
    assert user_after.detail.phone_number == new_phone_number

    log_entries_after = log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 2

    details_updated_log_entry = log_entries_after[1]
    assert details_updated_log_entry.event_type == 'user-details-updated'
    assert details_updated_log_entry.data == {
        'initiator_id': str(user.id),
        'old_zip_code': old_zip_code,
        'new_zip_code': new_zip_code,
        'old_city': old_city,
        'new_city': new_city,
        'old_street': old_street,
        'new_street': new_street,
    }


def test_update_user_real_name(site_app, make_user):
    old_first_names = 'Rainer'
    old_last_name = 'Zufall'

    new_first_names = 'Ryan R.'
    new_last_name = 'Wahnsinn'

    user = make_user(
        first_names=old_first_names,
        last_name=old_last_name,
    )
    user_detail = user_service.get_detail(user.id)

    log_entries_before = log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 1  # user creation

    # -------------------------------- #

    event = user_command_service.update_user_details(
        user.id,
        new_first_names,
        new_last_name,
        user_detail.date_of_birth,
        user_detail.country,
        user_detail.zip_code,
        user_detail.city,
        user_detail.street,
        user_detail.phone_number,
        user.id,
    )

    # -------------------------------- #

    user_after = user_command_service._get_user(user.id)
    assert user_after.detail.first_names == new_first_names
    assert user_after.detail.last_name == new_last_name

    log_entries_after = log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 2

    details_updated_log_entry = log_entries_after[1]
    assert details_updated_log_entry.event_type == 'user-details-updated'
    assert details_updated_log_entry.data == {
        'initiator_id': str(user.id),
        'old_first_names': old_first_names,
        'new_first_names': new_first_names,
        'old_last_name': old_last_name,
        'new_last_name': new_last_name,
    }


def test_remove_user_dob_and_phone_number(site_app, make_user):
    old_date_of_birth = date(1991, 9, 17)
    old_phone_number = '555-fake-anyway'

    user = make_user(
        date_of_birth=old_date_of_birth,
        phone_number=old_phone_number,
    )
    user_detail = user_service.get_detail(user.id)

    log_entries_before = log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 1  # user creation

    # -------------------------------- #

    event = user_command_service.update_user_details(
        user.id,
        user_detail.first_names,
        user_detail.last_name,
        None,
        user_detail.country,
        user_detail.zip_code,
        user_detail.city,
        user_detail.street,
        '',
        user.id,
    )

    # -------------------------------- #

    user_after = user_command_service._get_user(user.id)
    assert user_after.detail.date_of_birth is None
    assert user_after.detail.phone_number == ''

    log_entries_after = log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 2

    details_updated_log_entry = log_entries_after[1]
    assert details_updated_log_entry.event_type == 'user-details-updated'
    assert details_updated_log_entry.data == {
        'initiator_id': str(user.id),
        'old_date_of_birth': '1991-09-17',
        'new_date_of_birth': None,
        'old_phone_number': old_phone_number,
        'new_phone_number': '',
    }
