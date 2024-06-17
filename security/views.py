import os
from django.utils.crypto import get_random_string
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Channel
from .serializers import ChannelSerializer


BASE = settings.BASE
MODULUS = settings.MODULUS

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipient_username = self.request.data.get('recipient_user')
        recipient_user = User.objects.get(username=recipient_username)
        serializer.save(sender_user=self.request.user, recipient_user=recipient_user, name=get_random_string(length=12))

    def get_queryset(self):
        user = self.request.user
        return Channel.objects.filter(sender_user=user) | Channel.objects.filter(recipient_user=user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        channel = self.get_object()
        if channel.recipient_user == request.user:
            channel.accepted = True
            channel.save()
            return Response({'status': 'channel accepted'})
        return Response({'status': 'not authorized'}, status=403)

class SecretExchangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        channel = Channel.objects.get(pk=pk)
        user = request.user
        if channel.accepted and (channel.sender_user == user or channel.recipient_user == user):
            secret_key = int.from_bytes(os.urandom(32), byteorder='big')
            secret_value = pow(BASE, secret_key, MODULUS)
            if channel.sender_user == user:
                channel.initial_sender_secret = secret_value
                channel.save()
            elif channel.recipient_user == user:
                channel.initial_recipient_secret = secret_value
                channel.save()
            return Response({'secret_key': secret_key})
        return Response({'status': 'not authorized'}, status=403)

class KeyGenerationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        channel = Channel.objects.get(pk=pk)
        user = request.user
        secret_key = int(request.data.get('secret_key'))
        if channel.accepted and channel.initial_sender_secret and channel.initial_recipient_secret:
            if channel.sender_user == user:
                key = pow(channel.initial_recipient_secret, secret_key, MODULUS)
                return Response({'key': key})
            elif channel.recipient_user == user:
                key = pow(channel.initial_sender_secret, secret_key, MODULUS)
                return Response({'key': key})
        return Response({'status': 'not authorized or incomplete data'}, status=403)
