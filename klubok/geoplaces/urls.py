from django.urls import include, path

from geoplaces.views import PlaceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"places", PlaceViewSet, basename="place")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
