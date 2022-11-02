from django.contrib import admin
from django.urls import path
from geoplaces.urls import urlpatterns as geoplaces_urlpatterns

urlpatterns = [path("admin/", admin.site.urls)] + geoplaces_urlpatterns
