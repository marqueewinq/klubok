from uuid import uuid4
from constance import config
from django.contrib.gis.db import models as gis_models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from klubok.models import BaseModel


class Place(BaseModel):
    uuid = models.UUIDField(default=uuid4, primary_key=True)

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    url_img = models.URLField(max_length=512)

    rating = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    location = gis_models.PointField(geography=True, srid=4326)

    tags = models.ManyToManyField("geoplaces.PlaceTag", related_name="places")
    types = models.ManyToManyField("geoplaces.PlaceType", related_name="places")
    priceranges = models.ManyToManyField(
        "geoplaces.PlacePricerange", related_name="places"
    )

    promo_code = models.CharField(max_length=255, null=True, blank=True, default=None)

    def __str__(self) -> str:
        return self.title

    def update_rating(self) -> "Place":
        rating_score_window = config.RATING_SCORE_WINDOW

        rating_score_list = self.rating_submissions.order_by("-created_at")[
            :rating_score_window
        ].values_list("rating", flat=True)

        if len(rating_score_list) == 0:
            return self

        self.rating = int(sum(rating_score_list) / len(rating_score_list))
        return self


class BaseTextTagModel(BaseModel):
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title


class PlaceTag(BaseTextTagModel):
    pass


class PlaceType(BaseTextTagModel):
    pass


class PlacePricerange(BaseTextTagModel):
    pass


class PlaceRatingSubmission(BaseModel):
    uuid = models.UUIDField(default=uuid4, primary_key=True)

    rating = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    sender_id = models.CharField(max_length=255, unique=True)
    place = models.ForeignKey(
        "geoplaces.Place", related_name="rating_submissions", on_delete=models.CASCADE
    )
