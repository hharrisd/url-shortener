from django.urls import path
from shortener.views import LinkAPIView, redirector, LinkStatAPIView

urlpatterns = [
    path('submit/', LinkAPIView.as_view(), name='submit'),
    path('<slug:key>', redirector, name='redirector'),
    path('<slug:key__iexact>/stats', LinkStatAPIView.as_view(), name='stats'),
]
