import random
import string

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from geoplaces.fields import CharacterSeparatedField
from geoplaces.serializers import PlaceSearchSerializer
from geoplaces.models import Place, PlacePricerange, PlaceTag, PlaceType
from geoplaces.search import filter_queryset


def generate(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


class TestCharacterSeparatedManyField(APITestCase):
    def test_field_from_native_should_return_list_for_given_str(self):
        field = CharacterSeparatedField(child=serializers.CharField())
        assert field.to_internal_value("a,b,c") == ["a", "b", "c"]


class TestPlaceAPI(APITestCase):
    def setUp(self):
        user_data = {"username": "Me", "password": "pwd"}
        self.user = User.objects.create_user(**user_data)
        self.client.force_authenticate(user=self.user)
        self.client.post(reverse("rest_login"), data=user_data, format="json")
        self.token = Token.objects.get(user=self.user).key

        PlaceTag.objects.bulk_create(
            [PlaceTag(title="Sport"), PlaceTag(title="Food"), PlaceTag(title="18+")]
        )
        PlaceType.objects.bulk_create(
            [
                PlaceType(title="At home"),
                PlaceType(title="Party"),
                PlaceType(title="Cultural"),
            ]
        )
        PlacePricerange.objects.bulk_create(
            [PlacePricerange(title="$" * i) for i in range(3)]
        )

        self.n_places = 50
        for i in range(self.n_places):
            n_tags = random.randint(0, 3)
            n_types = random.randint(0, 3)
            n_priceranges = random.randint(0, 3)
            place = Place.objects.create(
                title=generate(8),
                description=generate(24),
                url_img=f"http://images.com/{generate(4)}",
                rating=random.randint(1, 5),
                location=Point(random.random() * 10, random.random() * 10 + 10),
            )
            place.tags.set(PlaceTag.objects.order_by("?")[:n_tags])
            place.types.set(PlaceType.objects.order_by("?")[:n_types])
            place.priceranges.set(PlacePricerange.objects.order_by("?")[:n_priceranges])

    def test_places_api(self):
        response = self.client.get(reverse("place-list"))
        self.assertEqual(200, response.status_code)

    def test_search_filter_queryset_text(self):
        random_place = Place.objects.order_by("?").first()
        data = {"text": random_place.title}
        serializer = PlaceSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        queryset = filter_queryset(queryset=Place.objects.all(), serializer=serializer)
        self.assertEqual(1, queryset.count())
        self.assertEqual(random_place.uuid, queryset.first().uuid)

    def test_search_filter_queryset_gis(self):
        def run_target(data):
            serializer = PlaceSearchSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return filter_queryset(queryset=Place.objects.all(), serializer=serializer)

        faraway_data = {
            "distance": 5.0,
            "location": {"type": "Point", "coordinates": [2.0, 2.0]},
        }
        queryset = run_target(faraway_data)
        self.assertEqual(0, queryset.count())

        nearby_data = {
            "distance": 1_000_000.0,
            "location": {"type": "Point", "coordinates": [10.0, 20.0]},
        }
        queryset = run_target(nearby_data)
        self.assertTrue(queryset.count() > 0)
