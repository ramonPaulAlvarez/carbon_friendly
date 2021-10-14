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
    def test_required_contact_fields(self, mock_send_mail):
        """Verify the required contact form fields are present."""
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
    def test_contact_email(self, mock_send_mail):
        """Verify contact form e-mail vaidation."""
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
    def test_smtp_service_configuration(self, mock_send_mail):
        """Verify that without a SMTP host configured the contact form raises a 503."""
        # Submit valid payload
        with override_settings(EMAIL_HOST=None):
            response = self.client.post(
                self.contact_url, data=self.valid_payload)

        # Verify that the request resulted in error
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE,
                         "Request did not fail as expected")
        self.assertContains(response, "SMTP service not yet configured",
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Verify no mail was sent
        self.assertFalse(mock_send_mail.called)


class ResourceViewsetTests(TestCase):
    """Test cases for the resources viewset."""

    def test_resource_get_list_paginated(self):
        """Verify that filtered resource requests get paginated responses."""
        response = self.client.get("/resources?limit=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify pagination fields are present
        expected_fields = ('count', 'next', 'previous', 'results')
        assert all(field in response.data for field in expected_fields)

        # Verify that first nested record has the expected fields
        record = response.data['results'][0]
        expected_fields = ('id', 'name', 'description', 'url',
                           'group', 'subgroup', 'icon', 'tags')
        assert all(field in record for field in expected_fields)

    def test_resources_get_list(self):
        """Verify that we can GET a list of resources."""
        # Verify that we can get at least one record
        response = self.client.get("/resources")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 1)

        # Verify first record has the expected fields
        resource = response.data[0]
        expected_fields = ('id', 'name', 'description', 'url',
                           'group', 'subgroup', 'icon', 'tags')
        assert all(field in resource for field in expected_fields)

    def test_resource_get_detail(self):
        """Verify that we cannot GET a resource directly."""
        # Fetch a resource to reference
        response = self.client.get("/resources")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 1)
        resource_id = response.data[0]['id']

        # Verify we get a 404 on the detail view
        response = self.client.get(f"/resources/{resource_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_resources_post(self):
        """Verify that we cannot POST a resource."""
        response = self.client.post("/resources", data={})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
