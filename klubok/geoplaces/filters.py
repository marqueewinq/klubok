from rest_framework import filters

from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q

from geoplaces.serializers import PlaceSearchSerializer


class GeoPlacesFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        serializer = PlaceSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return self._filter_queryset(queryset, serializer)

    @staticmethod
    def _filter_queryset(queryset, serializer):
        if "text" in serializer.validated_data:
            text = serializer.validated_data["text"]
            queryset = queryset.filter(
                Q(title__contains=text) | Q(description__contains=text)
            )

        if "rating" in serializer.validated_data:
            rating = serializer.validated_data["rating"]
            queryset = queryset.filter(rating__gte=rating)

        if "tags_titles" in serializer.validated_data:
            queryset = queryset.filter(
                tags__title__in=serializer.validated_data["tags_titles"]
            )
        if "types_titles" in serializer.validated_data:
            queryset = queryset.filter(
                types__title__in=serializer.validated_data["types_titles"]
            )
        if "priceranges_titles" in serializer.validated_data:
            queryset = queryset.filter(
                priceranges__title__in=serializer.validated_data["priceranges_titles"]
            )

        if (
            "location" in serializer.validated_data
            and "distance" in serializer.validated_data
        ):
            location = serializer.validated_data["location"]
            distance = serializer.validated_data["distance"]

            queryset = queryset.annotate(
                distance=Distance("location", location)
            ).filter(distance__lte=distance)

        return queryset.distinct()
