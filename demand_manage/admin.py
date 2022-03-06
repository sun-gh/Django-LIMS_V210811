from django.contrib import admin
from . import models


class DemandCollectAdmin(admin.ModelAdmin):
    list_display = ('demand_number', 'sponsor', 'department', 'demand_type', 'demand_describe')


admin.site.register(models.DemandCollect, DemandCollectAdmin)
admin.site.register(models.DemandDesign)
