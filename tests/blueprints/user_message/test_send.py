"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.services.brand import settings_service as brand_settings_service
from byceps.services.email import service as email_service
from byceps.services.user_message import service as user_message_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_site, \
    create_user, http_client, login_user


class SendUserMessageTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.brand = create_brand()
        party = create_party(self.brand.id)
        create_site(party.id)

        email_config_id = self.brand.id
        email_service.set_sender(email_config_id, 'noreply@example.com',
                                 sender_name='ACME Entertainment Convention')

    @patch('byceps.email.send')
    def test_send_when_logged_in_without_brand_contact_address(self,
                                                               send_email_mock):
        sender = create_user('Alice',
            user_id='a4903d8f-0bc6-4af9-aeb9-d7534a0a22e8',
            email_address='alice@example.com')
        recipient = create_user('Bob',
            email_address='bob@example.com')
        text = '''\
Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice
'''

        expected_response_location \
            = 'http://example.com/users/{}'.format(recipient.id)

        expected_email_sender = 'ACME Entertainment Convention <noreply@example.com>'
        expected_email_recipients = ['Bob <bob@example.com>']
        expected_email_subject = 'Mitteilung von Alice'
        expected_email_body = '''\
Hallo Bob,

Alice möchte dir folgende Mitteilung zukommen lassen:

---8<-------------------------------------

Hi Bob,

please don't forget to take out the trash.

kthxbye,
Alice

---8<-------------------------------------

Du kannst Alice hier antworten: http://example.com/user_messages/to/a4903d8f-0bc6-4af9-aeb9-d7534a0a22e8/create

-- 
Diese Mitteilung wurde über die Website der ACME Entertainment Convention gesendet.\
'''

        response = self.send_request(recipient.id, text,
                                     current_user_id=sender.id)

        assert response.status_code == 302
        assert response.location == expected_response_location

        send_email_mock.assert_called_once_with(
            expected_email_sender,
            expected_email_recipients,
            expected_email_subject,
            expected_email_body)

    @patch('byceps.email.send')
    def test_send_when_logged_in_with_brand_contact_address(self,
                                                            send_email_mock):
        brand_settings_service.create_setting(
            self.brand.id, 'contact_email_address', 'info@example.com')

        sender = create_user('Bob',
            user_id='11d72bab-3646-4199-b96c-e5e4c6f972bc',
            email_address='bob@example.com')
        recipient = create_user('Alice',
            email_address='alice@example.com')
        text = '''\
Hey Alice,

nice to hear from you.

Best,
Bob
'''

        expected_response_location \
            = 'http://example.com/users/{}'.format(recipient.id)

        expected_email_sender = 'ACME Entertainment Convention <noreply@example.com>'
        expected_email_recipients = ['Alice <alice@example.com>']
        expected_email_subject = 'Mitteilung von Bob'
        expected_email_body = '''\
Hallo Alice,

Bob möchte dir folgende Mitteilung zukommen lassen:

---8<-------------------------------------

Hey Alice,

nice to hear from you.

Best,
Bob

---8<-------------------------------------

Du kannst Bob hier antworten: http://example.com/user_messages/to/11d72bab-3646-4199-b96c-e5e4c6f972bc/create

-- 
Diese Mitteilung wurde über die Website der ACME Entertainment Convention gesendet.
Bei Fragen kontaktiere uns bitte per E-Mail an: info@example.com\
'''

        response = self.send_request(recipient.id, text,
                                     current_user_id=sender.id)

        assert response.status_code == 302
        assert response.location == expected_response_location

        send_email_mock.assert_called_once_with(
            expected_email_sender,
            expected_email_recipients,
            expected_email_subject,
            expected_email_body)

    def test_send_when_not_logged_in(self):
        recipient_id = '8e5037f6-3ca1-4981-b1e4-1998cbdf58e2'
        text = 'Hello, Eve!'

        response = self.send_request(recipient_id, text)

        assert response.status_code == 302
        assert response.location == 'http://example.com/authentication/login'

    # helpers

    def send_request(self, recipient_id, text, *, current_user_id=None):
        url = '/user_messages/to/{}/create'.format(recipient_id)

        form_data = {
            'body': text,
        }

        if current_user_id is not None:
            login_user(current_user_id)

        with http_client(self.app, user_id=current_user_id) as client:
            return client.post(url, data=form_data)
