from django import forms
from .models import SampleRecord, ProjectType, SampleType, MachineTime, SampleQuality, AdditionalItem, OperatePerson,\
    SampleStatus, ProjectInterrupt, Machine, ResponsiblePerson, SpeciesInfo
from customer.models import CustomerInfo


class SampleRecordForm(forms.ModelForm):
    # 定义样本登记表单
    project_type = forms.ModelChoiceField(queryset=ProjectType.objects.all(), label="项目类型",
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    # 样本类型为添加或修改时提供选项
    sample_type = forms.ModelChoiceField(queryset=SampleType.objects.all(), label="样本类型",
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    machine_time = forms.ModelChoiceField(queryset=MachineTime.objects.all(), label="机时类型", required=False,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    sample_amount = forms.IntegerField(label="样本数量", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sample_sender = forms.ModelChoiceField(queryset=CustomerInfo.objects.all(), label="送样人",
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    agent_id = forms.IntegerField(label="代理ID", max_value=999999, required=False,
                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))
    anti_fake_number = forms.CharField(label="防伪编号", required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control'}))
    sample_quality = forms.ModelChoiceField(queryset=SampleQuality.objects.all(), label="运送条件和质量",
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    addition_item = forms.ModelMultipleChoiceField(queryset=AdditionalItem.objects.all(), label="附加项目", required=False,
                                                   widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    receive_time = forms.DateTimeField(label="收样时间",
                                       input_formats=['%Y-%m-%dT%H:%M'],  # 负责保存到数据库的格式转化
                                       widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',  # 负责页面显示格式的转化
                                                                  attrs={'type': 'datetime-local',
                                                                         'class': 'form-control',
                                                                         'readonly': 'readonly'}))
    pro_start_date = forms.DateTimeField(label="项目启动时间",
                                         input_formats=['%Y-%m-%dT%H:%M'],
                                         required=False,
                                         widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                    attrs={'type': 'datetime-local',
                                                                           'class': 'form-control',
                                                                           'readonly': 'readonly'}))
    person_record = forms.CharField(label="登记人", widget=forms.TextInput(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = SampleRecord
        fields = [
            'project_type',
            'sample_amount',
            'sample_sender',
            'agent_id',
            'anti_fake_number',
            'sample_quality',
            'addition_item',
            'receive_time',
            'pro_start_date',
            'person_record',
            'note',
        ]


class PretreatStageForm(forms.ModelForm):
    # 定义前处理修改表单
    start_date = forms.DateTimeField(label="实验开始时间",
                                     input_formats=['%Y-%m-%dT%H:%M'],
                                     required=False,
                                     widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                attrs={'type': 'datetime-local',
                                                                       'class': 'form-control',
                                                                       'readonly': 'readonly'}))
    preexperiment_finish_date = forms.DateTimeField(label="质控完成时间",
                                                    input_formats=['%Y-%m-%dT%H:%M'],
                                                    required=False,
                                                    widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                               attrs={'type': 'datetime-local',
                                                                                      'class': 'form-control',
                                                                                      'readonly': 'readonly'}))
    pretreat_finish_date = forms.DateTimeField(label="前处理完成时间",
                                               input_formats=['%Y-%m-%dT%H:%M'],
                                               required=False,
                                               widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                          attrs={'type': 'datetime-local',
                                                                                 'class': 'form-control',
                                                                                 'readonly': 'readonly'}))
    # 以下4个元素为步骤1-4
    first_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True),
                                                          label="步骤一", required=False,
                                                          widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    second_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True),
                                                           label="步骤二", required=False,
                                                           widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    third_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True),
                                                          label="步骤三", required=False,
                                                          widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    fourth_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True),
                                                           label="步骤四", required=False,
                                                           widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    page_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True), label="跑胶",
                                                 required=False,
                                                 widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    sample_overplus = forms.NullBooleanField(label="样本剩余",
                                             widget=forms.NullBooleanSelect(attrs={'class': 'form-control'}))
    sample_overplus_status = forms.ModelMultipleChoiceField(
        queryset=SampleStatus.objects.all(), label="剩余样本状态", required=False, widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}))

    class Meta:
        model = SampleRecord
        fields = [
            'start_date',
            'preexperiment_finish_date',
            'pretreat_finish_date',
            # 以下4个元素为步骤1-4
            'first_operate_person',
            'second_operate_person',
            'third_operate_person',
            'fourth_operate_person',
            'page_person',
            'sample_overplus',
            'sample_overplus_status',
        ]


class TestStageForm(forms.ModelForm):
    # 定义质谱检测信息修改表单
    instrument_type = forms.ModelChoiceField(queryset=Machine.objects.all(), label="上机仪器",
                                             required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    date_test = forms.DateTimeField(label="上机时间",
                                    input_formats=['%Y-%m-%dT%H:%M'],
                                    required=False,
                                    widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                               attrs={'type': 'datetime-local',
                                                                      'class': 'form-control',
                                                                      'readonly': 'readonly'}))
    test_finish_date = forms.DateTimeField(label="下机时间",
                                           input_formats=['%Y-%m-%dT%H:%M'],
                                           required=False,
                                           widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                      attrs={'type': 'datetime-local',
                                                                             'class': 'form-control',
                                                                             'readonly': 'readonly'}))

    class Meta:
        model = SampleRecord
        fields = [
            'instrument_type',
            'date_test',
            'test_finish_date',
        ]


class AnalysisStageForm(forms.ModelForm):
    # 定义数据分析信息修改表单
    priority = forms.IntegerField(label="优先级", required=False, widget=forms.Select(choices=SampleRecord.priority_level,
                                  attrs={'class': 'form-control'}))
    project_interrupt = forms.ModelChoiceField(queryset=ProjectInterrupt.objects.all(), label="项目中断类型", required=False,
                                               widget=forms.Select(attrs={'class': 'form-control'}))
    responsible_person = forms.ModelChoiceField(queryset=ResponsiblePerson.objects.all(), label="项目负责人",
                                                required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    date_searchlib = forms.DateTimeField(label="搜库时间",
                                         input_formats=['%Y-%m-%dT%H:%M'],
                                         required=False,
                                         widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                    attrs={'type': 'datetime-local',
                                                                           'class': 'form-control',
                                                                           'readonly': 'readonly'}))
    date_send_report = forms.DateTimeField(label="报告发送时间",
                                           input_formats=['%Y-%m-%dT%H:%M'],
                                           required=False,
                                           widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                      attrs={'type': 'datetime-local',
                                                                             'class': 'form-control',
                                                                             'readonly': 'readonly'}))
    date_send_rawdata = forms.DateTimeField(label="原始数据发送",
                                            input_formats=['%Y-%m-%dT%H:%M'],
                                            required=False,
                                            widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                       attrs={'type': 'datetime-local',
                                                                              'class': 'form-control',
                                                                              'readonly': 'readonly'}))
    pro_deadline = forms.DateTimeField(label="项目截止时间",
                                       input_formats=['%Y-%m-%dT%H:%M'],
                                       widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                  attrs={'type': 'datetime-local',
                                                                         'class': 'form-control'}))
    status = forms.IntegerField(label="暂停或终止", widget=forms.Select(
        choices=SampleRecord.status_choices[-2:], attrs={'class': 'form-control'}))
    species = forms.ModelChoiceField(queryset=SpeciesInfo.objects.all(), label="物种", required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    protein_amount = forms.IntegerField(label="蛋白数量", required=False,
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = SampleRecord
        fields = [
            'priority',
            'project_interrupt',
            'responsible_person',
            'date_searchlib',
            'date_send_report',
            'date_send_rawdata',
            'pro_deadline',
            'status',
            'species',
            'protein_amount',
        ]


class EditAnalysisForm(forms.ModelForm):
    # 定义文件等信息修改表单（销售部专用）

    file_input = forms.FileField(label="相关文件", required=False, widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'class': 'form-control-file'}))

    class Meta:
        model = SampleRecord
        fields = [
            'files',
        ]


class SearchForm(forms.Form):
    # 定义搜索项表单
    project_type = forms.ModelChoiceField(queryset=ProjectType.objects.all(), label="项目类型", required=False,
                                          widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    sample_type = forms.ModelChoiceField(queryset=SampleType.objects.all(), label="样本类型", required=False,
                                         widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    status = forms.IntegerField(label="状态",
                                widget=forms.Select(choices=SampleRecord.status_choices,
                                                    attrs={'class': 'form-control form-control-sm'}))


class SpeciesInfoForm(forms.ModelForm):
    # 定义物种信息表单
    species = forms.CharField(label="物种", widget=forms.TextInput(attrs={'class': 'form-control'}))
    database = forms.CharField(label="数据库", widget=forms.TextInput(attrs={'class': 'form-control'}))
    entry_count = forms.IntegerField(label="条目数", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    creator = forms.CharField(label="添加人", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = SpeciesInfo
        fields = [
            'species',
            'database',
            'entry_count',
            'creator',
        ]
