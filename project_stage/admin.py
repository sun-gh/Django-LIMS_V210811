from django.contrib import admin
from . import models
from import_export import resources, fields
from import_export.admin import ExportMixin
from import_export.widgets import ForeignKeyWidget


# Register your models here.


class SampleRecordResource(resources.ModelResource):
    # 定义样本登记表导出功能
    project_type = fields.Field(
        column_name='project_type',
        # user 在本模型外键的字段名称
        attribute='project_type',
        # username 外键的里面的字段名
        widget=ForeignKeyWidget(models.ProjectType, 'project_name'))

    def __init__(self, input_contract=None):
        super(SampleRecordResource, self).__init__()
        field_list = models.SampleRecord._meta.fields
        self.verbose_name_dict = {}
        for i in field_list:
            self.verbose_name_dict[i.name] = i.verbose_name

    # 默认导入导出field的column_name为字段的名称，这里修改为字段的verbose_name
    def get_export_fields(self):
        fields = self.get_fields()
        for field in fields:
            field_name = self.get_field_name(field)
            # 如果有设置 verbose_name，则将 column_name 替换为 verbose_name, 否则维持原有的字段名。
            if field_name in self.verbose_name_dict.keys():
                field.column_name = self.verbose_name_dict[field_name]
        return fields

    class Meta:
        model = models.SampleRecord
        fields = ('project_num', 'project_type', 'sample_amount', 'receive_time', 'pro_start_date',
                  'start_date', 'preexperiment_finish_date', 'pretreat_finish_date', 'start_deadline', 'preexperiment_deadline',
                  'pretreat_deadline', 'date_test', 'test_finish_date', 'date_searchlib', 'date_send_report',
                  'date_send_rawdata', 'test_deadline', 'pro_deadline',)
        export_order = ('project_num', 'project_type', 'sample_amount', 'receive_time', 'pro_start_date',
                        'start_date', 'preexperiment_finish_date', 'pretreat_finish_date', 'start_deadline', 'preexperiment_deadline',
                        'pretreat_deadline', 'date_test', 'test_finish_date', 'date_searchlib', 'date_send_report',
                        'date_send_rawdata', 'test_deadline', 'pro_deadline',)


class SampleRecordAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('project_num', 'project_type', 'sample_amount', 'sample_type', 'sample_sender')
    resource_class = SampleRecordResource


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
# admin.site.register(models.ProjectInterrupt, ProjectInterruptAdmin)
admin.site.register(models.Machine)
admin.site.register(models.ResponsiblePerson)
