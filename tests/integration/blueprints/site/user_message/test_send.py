"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

import pytest

from tests.helpers import http_client, log_in_user


@pytest.fixture(scope='module')
def user_alice(make_user):
    return make_user('Alice', email_address='alice@users.test', locale='de')


@pytest.fixture(scope='module')
def user_bob(make_user):
    return make_user('Bob', email_address='bob@users.test', locale='en')


@patch('byceps.email.send')
def test_send_when_logged_in_without_brand_contact_address(
    send_email_mock, site_app, user_alice, user_bob
):
    sender_id = user_alice.id
    recipient_id = user_bob.id
    text = '''\
Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice
'''

    expected_response_location = f'http://www.acmecon.test/users/{recipient_id}'

    expected_email_sender = (
        'ACME Entertainment Convention <noreply@acmecon.test>'
    )
    expected_email_recipients = ['Bob <bob@users.test>']
    expected_email_subject = 'Message from Alice (via www.acmecon.test)'
    expected_email_body = f'''\
Hello Bob,

Alice has sent you the following message.

You can reply here: http://www.acmecon.test/user_messages/to/{user_alice.id}

ATTENTION: Do *not* reply to this email. Follow the link instead.

---8<-------------------------------------

Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice

---8<-------------------------------------

-- 
This message was sent via website www.acmecon.test.
If you have any questions, please contact us via email to: help@acmecon.test\
'''

    response = send_request(
        site_app, recipient_id, text, current_user_id=sender_id
    )

    assert response.status_code == 302
    assert response.location == expected_response_location

    assert_email(
        send_email_mock,
        expected_email_sender,
        expected_email_recipients,
        expected_email_subject,
        expected_email_body,
    )


@patch('byceps.email.send')
def test_send_when_logged_in_with_brand_contact_address(
    send_email_mock,
    site_app,
    user_alice,
    user_bob,
):
    sender_id = user_bob.id
    recipient_id = user_alice.id
    text = '''\
Hey Alice,

nice to hear from you.

Best,
Bob
'''

    expected_response_location = f'http://www.acmecon.test/users/{recipient_id}'

    expected_email_sender = (
        'ACME Entertainment Convention <noreply@acmecon.test>'
    )
    expected_email_recipients = ['Alice <alice@users.test>']
    expected_email_subject = 'Mitteilung von Bob (über www.acmecon.test)'
    expected_email_body = f'''\
Hallo Alice,

Bob möchte dir die folgende Mitteilung zukommen lassen.

Du kannst hier antworten: http://www.acmecon.test/user_messages/to/{user_bob.id}

ACHTUNG: Antworte *nicht* auf diese E-Mail, sondern folge dem Link.

---8<-------------------------------------

Hey Alice,

nice to hear from you.

Best,
Bob

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website www.acmecon.test gesendet.
Bei Fragen kontaktiere uns bitte per E-Mail an: help@acmecon.test\
'''

    response = send_request(
        site_app, recipient_id, text, current_user_id=sender_id
    )

    assert response.status_code == 302
    assert response.location == expected_response_location

    assert_email(
        send_email_mock,
        expected_email_sender,
        expected_email_recipients,
        expected_email_subject,
        expected_email_body,
    )


def test_send_when_not_logged_in(site_app):
    recipient_id = '8e5037f6-3ca1-4981-b1e4-1998cbdf58e2'
    text = 'Hello, Eve!'

    response = send_request(site_app, recipient_id, text)

    assert response.status_code == 302
    assert response.location == 'http://www.acmecon.test/authentication/log_in'


# helpers


def send_request(app, recipient_id, text, *, current_user_id=None):
    url = f'/user_messages/to/{recipient_id}'

    form_data = {'body': text}

    if current_user_id is not None:
        log_in_user(current_user_id)

    with http_client(app, user_id=current_user_id) as client:
        return client.post(url, data=form_data)


def assert_email(
    mock, expected_sender, expected_recipients, expected_subject, expected_body
):
    calls = mock.call_args_list
    assert len(calls) == 1

    pos_args, _ = calls[0]
    actual_sender, actual_recipients, actual_subject, actual_body = pos_args
    assert actual_sender == expected_sender
    assert actual_recipients == expected_recipients
    assert actual_subject == expected_subject
    assert actual_body == expected_body
