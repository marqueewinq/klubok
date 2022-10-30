from django.contrib import admin
from django.urls import include, path
from geoplaces.urls import urlpatterns as geoplaces_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("rest_auth.urls")),
] + geoplaces_urlpatterns
