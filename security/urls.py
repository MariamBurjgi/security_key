from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, SecretExchangeView, KeyGenerationView

router = DefaultRouter()
router.register(r'channels', ChannelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('secret-exchange/<int:pk>/', SecretExchangeView.as_view(), name='secret-exchange'),
    path('key-generation/<int:pk>/', KeyGenerationView.as_view(), name='key-generation'),
]
