from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from allauth.socialaccount.models import SocialApp
from tourpoint.models import TourPoint

class FacebookAuthTests(APITestCase):

    def setUp(self):
        social_app = SocialApp.objects.create(
            provider='facebook', name='snowtest',
            client_id='285691251852966',
            secret='138d6fe9b0791f506e36ce6f2e7840a3')
        social_app.sites.add(Site.objects.first())
        self.data = {'access_token': 'EAAED1a2VBqYBAIPHkFzIURwamz7frk5TjCbJy7zTLSpDbtZC1YtqzrwiBjRiMQP7Gt72J8fgXzZCGDyesdZCZBBZBELzHKNPZBYC2dXxqxyp5BU4Adb1RWg6VZALmZCzy8vb1UHGjY8aYlrgmRC4nmx2WqN0nzM25Uz45PqBbO7kqZBfgpnGl0Jft66rxnVQoYHsZD'}

    def test_facebook_authentication(self):
        """
        Ensure we can authenticate using facebook acess_token.
        """
        response = self.client.post(reverse('fb_login'), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['key'])


class TourPointTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='ADeuWcg6BG0WHQ==')
        self.client.force_login(self.user)
        

    def test_user_can_create_tour_point(self):
        data = {
            'name': 'Barigui Park',
            'category': 'park',
            'longitude': -25.4258213,
            'latitude': -49.3141436,
            'private': False
        }
        response = self.client.post(reverse('tourpoint-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_see_his_tourpoints(self):
        response = self.client.get(
            reverse('user-tourpoints', args=[self.user.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)