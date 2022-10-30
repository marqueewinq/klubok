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

        self.n_places = 5
        for i in range(self.n_places):
            n_tags = random.randint(1, 9)
            n_types = random.randint(1, 9)
            n_priceranges = random.randint(1, 9)
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

    @staticmethod
    def _run_target(data):
        serializer = PlaceSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return filter_queryset(queryset=Place.objects.all(), serializer=serializer)

    def test_search_filter_queryset_text(self):
        random_place = Place.objects.order_by("?").first()
        data = {"text": random_place.title}
        queryset = self._run_target(data)
        self.assertEqual(1, queryset.count())
        self.assertEqual(random_place.uuid, queryset.first().uuid)

    def test_search_filter_queryset_m2m(self):
        tags = PlaceTag.objects.order_by("?")[:2]
        data = {"tags__titles": [t.title for t in tags]}
        queryset = self._run_target(data)
        self.assertEqual(
            Place.objects.filter(tags__in=tags).distinct().count(), queryset.count()
        )

        types = PlaceType.objects.order_by("?")[:2]
        data = {"types__titles": [t.title for t in types]}
        queryset = self._run_target(data)
        self.assertEqual(
            Place.objects.filter(types__in=types).distinct().count(), queryset.count()
        )

        ranges = PlacePricerange.objects.order_by("?")[:2]
        data = {"priceranges__titles": [t.title for t in ranges]}
        queryset = self._run_target(data)
        self.assertEqual(
            Place.objects.filter(priceranges__in=ranges).distinct().count(),
            queryset.count(),
        )

    def test_search_filter_queryset_gis(self):
        faraway_data = {
            "distance": 5.0,
            "location": {"type": "Point", "coordinates": [2.0, 2.0]},
        }
        queryset = self._run_target(faraway_data)
        self.assertEqual(0, queryset.count())

        nearby_data = {
            "distance": 1_000_000.0,
            "location": {"type": "Point", "coordinates": [10.0, 20.0]},
            "rating": 1,
        }
        queryset = self._run_target(nearby_data)
        self.assertTrue(queryset.count() > 0)

    def test_search_filter_queryset_gis_realdata(self):
        my_location = (30.248_418_046_654_855, 59.943_254_885_423_31)
        places = [
            (30.304_845_367_774_753, 59.943_085_766_577_525),
            (30.325_740_996_093_44, 59.930_767_681_937_645),
        ]

        for idx, (lat, lon) in enumerate(places):
            Place.objects.create(
                title=generate(8),
                description=generate(24),
                url_img=f"http://images.com/{generate(4)}",
                rating=idx + 1,
                location=Point(lat, lon),
            )

        real_data_list = [
            (
                {
                    "distance": 3500.0,
                    "location": {"type": "Point", "coordinates": my_location},
                },
                1,
            ),
            (
                {
                    "distance": 5000.0,
                    "location": {"type": "Point", "coordinates": my_location},
                },
                2,
            ),
            (
                {
                    "distance": 5000.0,
                    "location": {"type": "Point", "coordinates": my_location},
                    "rating": 2,  # 2 and more
                },
                1,
            ),
            (
                {
                    "distance": 3000.0,
                    "location": {"type": "Point", "coordinates": my_location},
                },
                0,
            ),
        ]
        for real_data, expected_count in real_data_list:
            queryset = self._run_target(real_data)
            self.assertEqual(expected_count, queryset.count())
