from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from allauth.socialaccount.models import SocialApp
from tourpoint.models import TourPoint
from api import factories

# class FacebookAuthTests(APITestCase):

#     def setUp(self):
#         social_app = SocialApp.objects.create(
#             provider='facebook', name='snowtest',
#             client_id='285691251852966',
#             secret='138d6fe9b0791f506e36ce6f2e7840a3')
#         social_app.sites.add(Site.objects.first())
#         self.data = {'access_token': 'EAAED1a2VBqYBAIPHkFzIURwamz7frk5TjCbJy7zTLSpDbtZC1YtqzrwiBjRiMQP7Gt72J8fgXzZCGDyesdZCZBBZBELzHKNPZBYC2dXxqxyp5BU4Adb1RWg6VZALmZCzy8vb1UHGjY8aYlrgmRC4nmx2WqN0nzM25Uz45PqBbO7kqZBfgpnGl0Jft66rxnVQoYHsZD'}

#     def test_facebook_authentication(self):
#         """
#         Ensure we can authenticate using facebook acess_token.
#         """
#         response = self.client.post(reverse('fb_login'), self.data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(response.data['key'])


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
        user = factories.UserFactory.create()
        for i in range(10):
            factories.TourPointFactory(owner=user)
        self.client.force_login(user)
        response = self.client.get(
            reverse('user-tourpoints', args=[self.user.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_user_can_delete_his_own_tourpoints(self):
        data = {
            'name': 'Tangua Park',
            'category': 'park',
            'longitude': -25.4258213,
            'latitude': -49.3141436,
            'private': False
        }
        response = self.client.post(reverse('tourpoint-list'), data)
        response = self.client.delete(response.data['url'])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cant_delete_others_tourpoints(self):
        data = {
            'name': 'Oscar Niemeyer Museum',
            'category': 'museum',
            'longitude': -26.234565,
            'latitude': -50.984583,
            'private': False
        }
        response = self.client.post(reverse('tourpoint-list'), data)
        user = get_user_model().objects.create_user(
            username='testuser2', password='QtAT+8v7QLyfZQ==')
        self.client.force_login(user)
        response = self.client.delete(response.data['url'])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_can_see_only_restaurants(self):
        factories.TourPointFactory.create_batch(10)
        self.client.logout()
        response = self.client.get(reverse('tourpoint-list'))
        for tourpoint in response.data:
            self.assertEqual(tourpoint['category'], 'restaurant')

    def test_user_can_see_tour_points_in_a_radius_from_location(self):
        factories.TourPointFactory.create_batch(size=10)
        user = factories.UserFactory.create()
        self.client.force_login(user)
        response = self.client.get(reverse('tourpoint-search-list'), {
            'from': '-25.4283699,-49.2790737',
            'km': 5.0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data), 0)

    def test_anonymous_user_may_only_see_public_restaurants_in_a_radius_from_location(self):
        factories.TourPointFactory.create_batch(size=20)
        self.client.logout()
        response = self.client.get(reverse('tourpoint-search-list'), {
            'from': '-25.4283699,-49.2790737',
            'km': 5.0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for tourpoint in response.data:
            self.assertEqual(tourpoint['category'], 'restaurant')
            self.assertEqual(tourpoint['private'], False)
