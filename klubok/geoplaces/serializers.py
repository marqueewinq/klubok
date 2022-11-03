from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis
from django.core.validators import MinValueValidator, MaxValueValidator

from geoplaces.models import Place, PlaceRatingSubmission


class PlaceSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="title")
    types = serializers.SlugRelatedField(many=True, read_only=True, slug_field="title")
    priceranges = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="title"
    )

    class Meta:
        model = Place
        geo_field = "location"
        fields = [
            "uuid",
            "title",
            "description",
            "url_img",
            "rating",
            "location",
            "tags",
            "types",
            "priceranges",
            "created_at",
            "updated_at",
            "promo_code",
        ]


class PlaceSearchSerializer(serializers.Serializer):
    text = serializers.CharField(required=False)

    location = serializers_gis.GeometryField(required=False)
    distance = serializers.FloatField(required=False)

    rating = serializers.IntegerField(
        required=False, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    tags_titles = serializers.ListField(required=False)
    types_titles = serializers.ListField(required=False)
    priceranges_titles = serializers.ListField(required=False)

    def validate(self, data):
        if ("location" in data or "distance" in data) and not (
            "location" in data and "distance" in data
        ):
            raise serializers.ValidationError(
                "You must provide both location and distance"
            )
        return super().validate(data)


class PlaceIncreaseRatingSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)

    rating = serializers.IntegerField(
        required=True, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        model = PlaceRatingSubmission
        fields = ["uuid", "rating", "sender_id", "place"]
