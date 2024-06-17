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
    def test_channel_acceptance(self):
        channel = Channel.objects.create(sender_user=self.sender, recipient_user=self.recipient, name='testchannel')
        self.client.login(username='recipient', password='password')
        response = self.client.post(f'/api/channels/{channel.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        channel.refresh_from_db()
        self.assertTrue(channel.accepted)