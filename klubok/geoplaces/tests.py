import random
import string

from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from geoplaces.serializers import PlaceSearchSerializer
from geoplaces.models import (
    Place,
    PlacePricerange,
    PlaceTag,
    PlaceType,
    PlaceRatingSubmission,
)
from geoplaces.filters import GeoPlacesFilter


from constance import config


def generate(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


class TestPlaceAPI(APITestCase):
    def setUp(self):
        n_tags = 4
        PlaceTag.objects.bulk_create(
            [
                PlaceTag(title="Sport"),
                PlaceTag(title="Food"),
                PlaceTag(title="18+"),
                PlaceTag(title="Between"),
            ]
        )
        n_types = 5
        PlaceType.objects.bulk_create(
            [
                PlaceType(title="At home"),
                PlaceType(title="Party"),
                PlaceType(title="I see you are"),
                PlaceType(title="Cultural"),
                PlaceType(title="As well"),
            ]
        )
        n_priceranges = 5
        PlacePricerange.objects.bulk_create(
            [PlacePricerange(title="$" * i) for i in range(1, 5)]
        )

        self.n_places = 5
        for i in range(self.n_places):
            n_select_tags = random.randint(0, n_tags)
            n_select_types = random.randint(0, n_types)
            n_select_priceranges = random.randint(0, n_priceranges)
            place = Place.objects.create(
                title=generate(8),
                description=generate(24),
                url_img=f"http://images.com/{generate(4)}",
                rating=random.randint(1, 5),
                location=Point(random.random() * 10, random.random() * 10 + 10),
            )
            place.tags.set(PlaceTag.objects.order_by("?")[:n_select_tags])
            place.types.set(PlaceType.objects.order_by("?")[:n_select_types])
            place.priceranges.set(
                PlacePricerange.objects.order_by("?")[:n_select_priceranges]
            )

    def test_places_api(self):
        response = self.client.get(reverse("place-list"))
        self.assertEqual(200, response.status_code)

        place = Place.objects.order_by("?").first()
        response = self.client.get(reverse("place-detail", kwargs={"pk": place.pk}))
        self.assertEqual(200, response.status_code)

    def _run_target_against_api(self, data):
        response = self.client.get(reverse("place-list"), data=data)
        self.assertEqual(200, response.status_code, response.json())

        serializer = PlaceSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        queryset = GeoPlacesFilter._filter_queryset(
            queryset=Place.objects.prefetch_related(
                "tags", "types", "priceranges"
            ).all(),
            serializer=serializer,
        )
        self.assertEqual(response.json()["count"], queryset.count())

        return queryset

    @staticmethod
    def _run_target_against_filter(data):
        serializer = PlaceSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return GeoPlacesFilter._filter_queryset(
            queryset=Place.objects.prefetch_related(
                "tags", "types", "priceranges"
            ).all(),
            serializer=serializer,
        )

    def test_search_filter_queryset_text(self):
        random_place = Place.objects.order_by("?").first()
        data = {"text": random_place.title}
        queryset = self._run_target_against_api(data)
        self.assertEqual(1, queryset.count())
        self.assertEqual(random_place.uuid, queryset.first().uuid)

    def test_search_filter_queryset_m2m(self):
        # Combining multiple aggregations will yield the wrong results
        #  because joins are used instead of subqueries -- we use
        #  len() instead of count() because of this
        tags = list(PlaceTag.objects.order_by("?")[:2])
        data = {"tags_titles": [t.title for t in tags]}
        queryset = self._run_target_against_api(data)
        self.assertEqual(
            len(Place.objects.filter(tags__in=tags).distinct()), len(queryset)
        )

        types = list(PlaceType.objects.order_by("?")[:2])
        data = {"types_titles": [t.title for t in types]}
        queryset = self._run_target_against_api(data)
        self.assertEqual(
            len(Place.objects.filter(types__in=types).distinct()), len(queryset)
        )

        ranges = list(PlacePricerange.objects.order_by("?")[:2])
        data = {"priceranges_titles": [t.title for t in ranges]}
        queryset = self._run_target_against_api(data)
        self.assertEqual(
            len(Place.objects.filter(priceranges__in=ranges).distinct()), len(queryset)
        )

    def test_search_filter_queryset_gis(self):
        faraway_data = {
            "distance": 5.0,
            "location": {"type": "Point", "coordinates": [2.0, 2.0]},
        }
        queryset = self._run_target_against_filter(faraway_data)
        self.assertEqual(0, queryset.count())

        nearby_data = {
            "distance": 1_000_000.0,
            "location": {"type": "Point", "coordinates": [10.0, 20.0]},
            "rating": 1,
        }
        queryset = self._run_target_against_filter(nearby_data)
        self.assertTrue(queryset.count() > 0)

    def test_search_filter_queryset_gis_realdata(self):
        my_location = (30.248_418_046_654_855, 59.943_254_885_423_31)
        places = [
            (30.304_845_367_774_753, 59.943_085_766_577_525),
            (30.325_740_996_093_44, 59.930_767_681_937_645),
        ]  # some points on a Vasilyevsky island

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
            queryset = self._run_target_against_filter(real_data)
            self.assertEqual(expected_count, queryset.count())

    def test_place_update_rating(self):
        place = Place.objects.order_by("?").first()

        old_rating = place.rating
        place.update_rating()
        self.assertEqual(old_rating, place.rating)

        def _check(n_ratings):
            for _ in range(n_ratings):
                PlaceRatingSubmission.objects.create(
                    place=place, rating=random.randint(0, 5), sender_id=generate(8)
                )
            rating_score_list = PlaceRatingSubmission.objects.order_by("-created_at")[
                : config.RATING_SCORE_WINDOW
            ].values_list("rating", flat=True)
            avg_rating = int(sum(rating_score_list) / len(rating_score_list))

            place.update_rating()
            self.assertEqual(avg_rating, place.rating)

        _check(config.RATING_SCORE_WINDOW // 2)
        _check(config.RATING_SCORE_WINDOW * 2)

    def test_submit_rating_api(self):
        place = Place.objects.order_by("?").first()
        new_rating = random.randint(0, 5)
        data = {
            "sender_id": generate(16),
            "place": str(place.uuid),
            "rating": new_rating,
        }
        response = self.client.post(
            reverse("place-submit-rating", kwargs={"pk": place.pk}), data=data
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.json())

        self.assertEqual(1, PlaceRatingSubmission.objects.filter(place=place).count())
