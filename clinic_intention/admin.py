from django.contrib import admin
from . import models


class ClinicIntentionAdmin(admin.ModelAdmin):
    list_display = ('intention_number', 'customer_name', 'disease_type', 'plan_needed', 'add_person')


admin.site.register(models.SampleType)
admin.site.register(models.DemandType)
admin.site.register(models.FollowUpRecord)
admin.site.register(models.ClinicIntention, ClinicIntentionAdmin)

