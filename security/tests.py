from .models import Channel
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class ChannelAPITest(APITestCase):
    def setUp(self):
            self.sender = User.objects.create_user(username='sender', password='password')
            self.recipient = User.objects.create_user(username='recipient', password='password')
    def test_channel_creation(self):
                self.client.login(username='sender', password='password')
                response = self.client.post('/api/channels/', {'recipient_user': 'recipient'})
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(Channel.objects.count(), 1)
