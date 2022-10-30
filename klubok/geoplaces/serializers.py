from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis

from geoplaces.models import Place
from geoplaces.fields import CharacterSeparatedField


class PlaceSerializer(serializers.ModelSerializer):
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
        ]


class PlaceSearchSerializer(serializers.Serializer):
    text = serializers.CharField(required=False)

    location = serializers_gis.GeometryField(required=False)
    distance = serializers.FloatField(required=False)

    rating = serializers.IntegerField(required=False)

    tags_titles = CharacterSeparatedField(required=False, separator=",")
    types_titles = CharacterSeparatedField(required=False, separator=",")
    priceranges_titles = CharacterSeparatedField(required=False, separator=",")

    def validate(self, data):
        if ("location" in data or "distance" in data) and not (
            "location" in data and "distance" in data
        ):
            raise serializers.ValidationError(
                "You must provide both location and distance"
            )
        return super().validate(data)
