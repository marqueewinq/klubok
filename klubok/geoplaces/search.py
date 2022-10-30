from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from geoplaces.serializers import PlaceSearchSerializer


def filter_queryset(queryset, serializer: PlaceSearchSerializer):
    if "text" in serializer.validated_data:
        text = serializer.validated_data["text"]
        queryset = queryset.filter(
            Q(title__contains=text) | Q(description__contains=text)
        )

    if "rating" in serializer.validated_data:
        rating = serializer.validated_data["rating"]
        queryset = queryset.filter(rating__gte=rating)

    if "tags_titles" in serializer.validated_data:
        tags_titles = serializer.validated_data["tags_titles"]

        queryset = queryset.filter(tags__title__in=tags_titles)

    # TODO: add the same filters on: types, priceranges, promos

    if (
        "location" in serializer.validated_data
        and "distance" in serializer.validated_data
    ):
        location = serializer.validated_data["location"]
        distance = serializer.validated_data["distance"]

        queryset = queryset.annotate(distance=Distance("location", location)).filter(
            distance__lte=distance
        )

    return queryset
