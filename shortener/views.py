from django.db.models import F
from django.http import HttpResponseRedirect
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializer import LinkSerializer, LinkStatSerializer
from .utils import create_unique_random_key
from .models import Link
from django.utils import timezone


class LinkAPIView(generics.ListCreateAPIView):
    """Creates short Links"""
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)

        if 'key' in serializer.validated_data.keys() and serializer.validated_data['key']:
            key = serializer.validated_data['key']
        else:
            key = create_unique_random_key()

        serializer.save(key=key, created_by=self.request.user)

    def get_queryset(self, *args, **kwargs):
        return Link.objects.filter(created_by=self.request.user)


class LinkStatAPIView(generics.RetrieveAPIView):
    """Retrieves the link statistics by shortcode"""
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Link.objects.all()
    serializer_class = LinkStatSerializer
    lookup_field = 'key__iexact'


@api_view(['GET', 'HEAD'])
def redirector(request, key):
    """If the key exists, redirects to the original URL and counts the visit"""
    if link_obj := Link.objects.filter(key__iexact=key).first():
        link_obj.clicks = F('clicks') + 1
        link_obj.last_visit = timezone.now()
        link_obj.save()
        return HttpResponseRedirect(link_obj.url, status=status.HTTP_302_FOUND)
    return Response(status=status.HTTP_404_NOT_FOUND)
