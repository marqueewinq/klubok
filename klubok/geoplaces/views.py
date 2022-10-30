from rest_framework import viewsets

from geoplaces.models import Place
from geoplaces.serializers import PlaceSearchSerializer, PlaceSerializer
from geoplaces.search import filter_queryset


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows places to be viewed or searched.

    Include additional query parameters to perform filter on the objects:

     - text: str
     - location: geojson
     - distance: float, in meters
     - rating: int, in range 1..5
     - tags_titles: list of str
     - types_titles: list of str
     - priceranges_titles: list of str
    """

    serializer_class = PlaceSerializer

    def get_queryset(self):
        serializer = PlaceSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        return filter_queryset(
            queryset=Place.objects.all().order_by("-updated_at"), serializer=serializer
        )
