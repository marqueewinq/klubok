from rest_framework import viewsets

from geoplaces.models import Place
from geoplaces.serializers import PlaceSearchSerializer, PlaceSerializer
from geoplaces.search import filter_queryset


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows places to be viewed.
    """

    serializer_class = PlaceSerializer

    def get_queryset(self):
        serializer = PlaceSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        return filter_queryset(
            queryset=Place.objects.all().order_by("-updated_at"), serializer=serializer
        )
