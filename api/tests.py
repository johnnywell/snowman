from django.urls import reverse
from django.contrib.sites.models import Site
from rest_framework import status
from rest_framework.test import APITestCase
from allauth.socialaccount.models import SocialApp


class FacebookAuthTests(APITestCase):

    def setUp(self):
        social_app = SocialApp.objects.create(
            provider='facebook', name='snowtest',
            client_id='285691251852966',
            secret='138d6fe9b0791f506e36ce6f2e7840a3')
        social_app.sites.add(Site.objects.first())

    def test_facebook_authentication(self):
        """
        Ensure we can authenticate using facebook acess_token.
        """
        url = reverse('fb_login')
        data = {'access_token': (
            'EAAED1a2VBqYBAO1JEwrjsoGNw1KnrZAYA8llrACiPEXJjMLqYLx1LkX83b02SldTy'
            '5ai0sniWeM2llZCJTdZBhgLEEyGyYrorMnZCiCl9ZAr5TuNVsfb48zZCyNcRXECcco'
            '5M2y6VwvzdzEyfZCHyXs4KJZCK4j22YLWQEAPKR6HUNA8kl87SZBWYH02NJMTkzWcZD'
            )}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['key'])