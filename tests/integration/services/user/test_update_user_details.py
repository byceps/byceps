"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

from byceps.services.user import (
    user_command_service,
    user_log_service,
    user_service,
)
from byceps.services.user.events import UserDetailsUpdatedEvent


def test_update_user_address(database, make_user):
    old_first_name = 'Rainer'
    old_last_name = 'Zufall'
    old_date_of_birth = None
    old_country = 'Germany'
    old_postal_code = '22999'
    old_city = 'Büttenwarder'
    old_street = 'Dorfweg 23'
    old_phone_number = None

    new_first_name = 'Rainer'
    new_last_name = 'Zufall'
    new_date_of_birth = None
    new_country = 'Germany'
    new_postal_code = '20099'
    new_city = 'Hamburg'
    new_street = 'Kirchenallee 1'
    new_phone_number = None

    user = make_user(
        first_name=old_first_name,
        last_name=old_last_name,
        date_of_birth=old_date_of_birth,
        country=old_country,
        postal_code=old_postal_code,
        city=old_city,
        street=old_street,
        phone_number=old_phone_number,
    )

    log_entries_before = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 2  # user creation

    # -------------------------------- #

    event = user_command_service.update_user_details(
        user.id,
        new_first_name,
        new_last_name,
        new_date_of_birth,
        new_country,
        new_postal_code,
        new_city,
        new_street,
        new_phone_number,
        user,
    )

    # -------------------------------- #

    assert isinstance(event, UserDetailsUpdatedEvent)
    assert event.initiator is not None
    assert event.initiator.id == user.id
    assert event.initiator.screen_name == user.screen_name
    assert event.user.id == user.id
    assert event.user.screen_name == user.screen_name

    user_after = user_service.get_db_user(user.id)
    assert user_after.detail.first_name == new_first_name
    assert user_after.detail.last_name == new_last_name
    assert user_after.detail.date_of_birth == new_date_of_birth
    assert user_after.detail.country == new_country
    assert user_after.detail.postal_code == new_postal_code
    assert user_after.detail.city == new_city
    assert user_after.detail.street == new_street
    assert user_after.detail.phone_number == new_phone_number

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 3

    details_updated_log_entry = log_entries_after[-1]
    assert details_updated_log_entry.event_type == 'user-details-updated'
    assert details_updated_log_entry.data == {
        'initiator_id': str(user.id),
        'old_postal_code': old_postal_code,
        'new_postal_code': new_postal_code,
        'old_city': old_city,
        'new_city': new_city,
        'old_street': old_street,
        'new_street': new_street,
    }


def test_update_user_real_name(database, make_user):
    old_first_name = 'Rainer'
    old_last_name = 'Zufall'

    new_first_name = 'Ryan R.'
    new_last_name = 'Wahnsinn'

    user = make_user(
        first_name=old_first_name,
        last_name=old_last_name,
    )
    user_detail = user_service.get_detail(user.id)

    log_entries_before = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 2  # user creation

    # -------------------------------- #

    user_command_service.update_user_details(
        user.id,
        new_first_name,
        new_last_name,
        user_detail.date_of_birth,
        user_detail.country,
        user_detail.postal_code,
        user_detail.city,
        user_detail.street,
        user_detail.phone_number,
        user,
    )

    # -------------------------------- #

    user_after = user_service.get_db_user(user.id)
    assert user_after.detail.first_name == new_first_name
    assert user_after.detail.last_name == new_last_name

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 3

    details_updated_log_entry = log_entries_after[-1]
    assert details_updated_log_entry.event_type == 'user-details-updated'
    assert details_updated_log_entry.data == {
        'initiator_id': str(user.id),
        'old_first_name': old_first_name,
        'new_first_name': new_first_name,
        'old_last_name': old_last_name,
        'new_last_name': new_last_name,
    }


def test_remove_user_dob_and_phone_number(database, make_user):
    old_date_of_birth = date(1991, 9, 17)
    old_phone_number = '555-fake-anyway'

    user = make_user(
        date_of_birth=old_date_of_birth,
        phone_number=old_phone_number,
    )
    user_detail = user_service.get_detail(user.id)

    log_entries_before = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 2  # user creation

    # -------------------------------- #

    user_command_service.update_user_details(
        user.id,
        user_detail.first_name,
        user_detail.last_name,
        None,
        user_detail.country,
        user_detail.postal_code,
        user_detail.city,
        user_detail.street,
        '',
        user,
    )

    # -------------------------------- #

    user_after = user_service.get_db_user(user.id)
    assert user_after.detail.date_of_birth is None
    assert user_after.detail.phone_number == ''

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 3

    details_updated_log_entry = log_entries_after[-1]
    assert details_updated_log_entry.event_type == 'user-details-updated'
    assert details_updated_log_entry.data == {
        'initiator_id': str(user.id),
        'old_date_of_birth': '1991-09-17',
        'new_date_of_birth': None,
        'old_phone_number': old_phone_number,
        'new_phone_number': '',
    }
