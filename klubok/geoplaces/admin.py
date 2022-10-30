from django.contrib import admin
from geoplaces.models import Place, PlacePricerange, PlaceTag, PlaceType


class PlaceAdmin(admin.ModelAdmin):
    pass


class PlaceTagAdmin(admin.ModelAdmin):
    pass


class PlaceTypeAdmin(admin.ModelAdmin):
    pass


class PlacePricerangeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceTag, PlaceTagAdmin)
admin.site.register(PlaceType, PlaceTypeAdmin)
admin.site.register(PlacePricerange, PlacePricerangeAdmin)
