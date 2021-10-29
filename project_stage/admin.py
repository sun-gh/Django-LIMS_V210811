from django.contrib import admin
from . import models

# Register your models here.


class SampleRecordAdmin(admin.ModelAdmin):
    list_display = ('project_num', 'project_type', 'sample_amount', 'sample_type', 'sample_sender')


class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'total_cycle', 'start_deadline', 'pre_experiment_cycle', 'pre_process_cycle',
                    'test_cycle', 'analysis_cycle')


admin.site.register(models.SampleType)
admin.site.register(models.MachineTime)
admin.site.register(models.SampleQuality)
admin.site.register(models.AdditionalItem)
admin.site.register(models.ProjectType, ProjectTypeAdmin)
admin.site.register(models.SampleRecord, SampleRecordAdmin)
admin.site.register(models.OperatePerson)
admin.site.register(models.SampleStatus)
admin.site.register(models.ProjectInterrupt)
admin.site.register(models.Machine)
admin.site.register(models.ResponsiblePerson)
