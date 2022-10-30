from uuid import uuid4

from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
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

    def __str__(self):
        return f"{self.title}"


class BaseTextTagModel(BaseModel):
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class PlaceTag(BaseTextTagModel):
    pass


class PlaceType(BaseTextTagModel):
    pass


class PlacePricerange(BaseTextTagModel):
    pass
