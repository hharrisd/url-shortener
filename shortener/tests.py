import base64
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import HTTP_HEADER_ENCODING, status
from rest_framework.test import APITestCase


def get_b64_credentials(credentials: str) -> str:
    return base64.b64encode(
        credentials.encode(HTTP_HEADER_ENCODING)
    ).decode(HTTP_HEADER_ENCODING)


class LinkShortenerTestCase(APITestCase):
    def setUp(self) -> None:
        self.user1_raw_pass = 'testpass123'
        self.user1 = get_user_model().objects.create_user(
            username='user1',
            email='testuser1@email.com',
            password=self.user1_raw_pass
        )

        self.credentials1 = get_b64_credentials(f"{self.user1.username}:{self.user1_raw_pass}")

        self.data_url_key = {'url': 'https://www.google.com/', 'key': 'google'}
        self.data_url = {'url': 'https://www.google.com/'}

    def test_create_link_without_shortcode_proposed(self):
        """
        Given an authenticated user, ensures that the shortened URL is created with a generated shortcode
        """
        response = self.client.post(reverse('submit'), data=self.data_url,
                                    HTTP_AUTHORIZATION=f"Basic {self.credentials1}", )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['key']), 6)
        self.assertEqual(response.data['created_by'], self.user1.username)
        self.assertEqual(response.data['shortened_url'], f"{settings.BASE_DOMAIN}/{response.data['key']}")

    def test_create_link_with_shortcode_proposed(self):
        """
        Given an authenticated user, ensures that the shortened URL is created with th proposed shortcode
        """
        response = self.client.post(reverse('submit'), data=self.data_url_key,
                                    HTTP_AUTHORIZATION=f"Basic {self.credentials1}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.user1.username)
        self.assertEqual(response.data['key'], self.data_url_key['key'])
        self.assertEqual(response.data['shortened_url'], f"{settings.BASE_DOMAIN}/{self.data_url_key['key']}")

    def test_avoid_create_link_with_unavailable_shortcode(self):
        """
        Given an authenticated user, if the proposed alias already exists returns an error
        """
        self.client.post(reverse('submit'), data=self.data_url_key, HTTP_AUTHORIZATION=f"Basic {self.credentials1}")
        response = self.client.post(reverse('submit'), data=self.data_url_key,
                                    HTTP_AUTHORIZATION=f"Basic {self.credentials1}")

        self.assertContains(response, status_code=status.HTTP_400_BAD_REQUEST, text='The proposed key already exists.')

    def test_shortcode_has_required_length(self):
        """
        Given an authenticated user, the proposed alias length must have 4 characters at least
        """
        data = {'url': 'https://test.com', 'key': 'abc'}
        response = self.client.post(reverse('submit'), data=data, HTTP_AUTHORIZATION=f"Basic {self.credentials1}")

        self.assertContains(response, status_code=status.HTTP_400_BAD_REQUEST,
                            text='Ensure this field has at least 4 characters.')

    def test_shortcode_redirects_properly(self):
        """
        Ensure that a shortcode (proposed or generated) is redirecting to the expected URL
        """
        self.client.post(reverse('submit'), data=self.data_url_key, HTTP_AUTHORIZATION=f"Basic {self.credentials1}")
        response = self.client.get(reverse('redirector', args=[self.data_url_key['key']]))
        self.assertRedirects(response, expected_url=self.data_url_key['url'], fetch_redirect_response=False)

        created = self.client.post(reverse('submit'), data=self.data_url,
                                   HTTP_AUTHORIZATION=f"Basic {self.credentials1}")
        response = self.client.get(reverse('redirector', args=[created.data['key']]))
        self.assertRedirects(response, expected_url=self.data_url['url'], fetch_redirect_response=False)

    def test_non_existing_shortcode_returns_not_found(self):
        """
        Ensure that a non-existing shortcode returns not found error on retrieving
        """
        response = self.client.get(reverse('redirector', args=["any-shortcode"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_shortcode_redirects_is_case_insensitive(self):
        """
        Ensure that retrieving a URL by shortcode is case-insensitive
        """
        self.client.post(reverse('submit'), data=self.data_url_key, HTTP_AUTHORIZATION=f"Basic {self.credentials1}")
        response_lower = self.client.get(reverse('redirector', args=[self.data_url_key['key'].lower()]))
        response_upper = self.client.get(reverse('redirector', args=[self.data_url_key['key'].upper()]))
        self.assertEqual(response_lower.url, response_upper.url)

    def test_shortcode_stats(self):
        """
        Given an authenticated user, verify a shortcode's stats
        """
        self.client.post(reverse('submit'), data=self.data_url_key, HTTP_AUTHORIZATION=f"Basic {self.credentials1}")

        self.client.get(reverse('redirector', args=[self.data_url_key['key']]))
        time.sleep(2)
        self.client.get(reverse('redirector', args=[self.data_url_key['key']]))
        time.sleep(2)
        self.client.get(reverse('redirector', args=[self.data_url_key['key']]))

        response = self.client.get(reverse('stats', args=[self.data_url_key['key']]),
                                   HTTP_AUTHORIZATION=f"Basic {self.credentials1}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clicks'], 3)
        self.assertEqual(response.data['target_url'], self.data_url_key['url'])
        self.assertGreater(response.data['last_visit'], response.data['created_at'])
