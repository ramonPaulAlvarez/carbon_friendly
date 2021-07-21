import mock
from django.test import TestCase, override_settings
from rest_framework import status


class ContactViewsetTests(TestCase):
    """Test cases for the contact viewset."""

    def setUp(self):
        """Perform test data setup."""
        self.contact_url = "/contact"
        self.valid_payload = {
            "from_email": "user@host.net",
            "subject": "Subject",
            "message": "Message"
        }

    @mock.patch('core.views.send_mail')
    def test_required_fields(self, mock_send_mail):
        """Verify contact required fields."""
        payload = self.valid_payload.copy()

        for field in ("from_email", "subject", "message"):
            # Remove required field
            del payload[field]

            # Verify that the payload is rejected
            with override_settings(EMAIL_HOST="localhost"):
                response = self.client.post(self.contact_url, data=payload)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, f"{field} was not required!")
            self.assertContains(response, "This field may not be null.",
                                status_code=status.HTTP_400_BAD_REQUEST)

            # Verify no mail was sent
            self.assertFalse(mock_send_mail.called)
            mock_send_mail.reset_mock()

            # Restore valid value for field
            payload[field] = self.valid_payload[field]

    @mock.patch('core.views.send_mail')
    def test_email_validator(self, mock_send_mail):
        """Verify contact e-mail validation."""
        payload = self.valid_payload.copy()

        for invalid_email in ("user@host", "@host.net", "host.net"):
            payload["from_email"] = invalid_email

            # Verify that the payload is rejected
            with override_settings(EMAIL_HOST="localhost"):
                response = self.client.post(self.contact_url, data=payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             f"{invalid_email} was not rejected!")
            self.assertContains(response, "Enter a valid email address.",
                                status_code=status.HTTP_400_BAD_REQUEST)

            # Verify no mail was sent
            self.assertFalse(mock_send_mail.called)
            mock_send_mail.reset_mock()

        for valid_email in ("user@host.net", "user@host.co.uk"):
            payload["from_email"] = valid_email

            # Verify that the payload is rejected
            response = self.client.post(self.contact_url, data=payload)
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             f"{valid_email} was not considered valid!")
            self.assertContains(response, "Message sent!")

            # Verify no mail was sent
            self.assertTrue(mock_send_mail.called)
            mock_send_mail.reset_mock()

    @mock.patch('core.views.send_mail')
    def test_smtp_service_disabled(self, mock_send_mail):
        """Verify that if the SMTP host isn't configured we don't attempt to send an e-mail."""
        # Submit valid payload
        with override_settings(EMAIL_HOST=None):
            response = self.client.post(
                self.contact_url, data=self.valid_payload)

        # Verify that the request resulted in error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR,
                         "Request did not fail as expected")
        self.assertContains(response, "SMTP service not yet configured",
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Verify no mail was sent
        self.assertFalse(mock_send_mail.called)
