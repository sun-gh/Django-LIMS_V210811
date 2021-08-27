from django import forms
from .models import SampleRecord, ProjectType, SampleType, MachineTime, SampleQuality, AdditionalItem, OperatePerson,\
    SampleStatus, ProjectInterrupt, Machine
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
    sample_quality = forms.ModelChoiceField(queryset=SampleQuality.objects.all(), label="样本质量",
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    addition_item = forms.ModelMultipleChoiceField(queryset=AdditionalItem.objects.all(), label="附加项目", required=False,
                                                   widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    receive_date = forms.DateField(label="收样日期",  widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    person_record = forms.CharField(label="登记人", widget=forms.TextInput(attrs={'class': 'form-control'}))
    project_source = forms.IntegerField(label="项目来源", required=False, widget=forms.Select(
        choices=SampleRecord.source_choice, attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    file_input = forms.FileField(label="相关文件", required=False, widget=forms.ClearableFileInput(
                                attrs={'multiple': True, 'class': 'form-control-file'}))

    class Meta:
        model = SampleRecord
        fields = [
            # 'project_num',
            'project_type',
            # 'sample_type',
            # 'machine_time',
            'sample_amount',
            'sample_sender',
            'sample_quality',
            'addition_item',
            'receive_date',
            'person_record',
            'project_source',
            'note',
            'files',
        ]


class PretreatStageForm(forms.ModelForm):
    # 定义前处理修改表单
    priority = forms.IntegerField(label="优先级", required=False, widget=forms.Select(choices=SampleRecord.priority_level,
                                                                                   attrs={'class': 'form-control'}))
    start_date = forms.DateField(label="项目启动时间", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    preexperiment_finish_date = forms.DateField(label="预实验完成时间", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    pretreat_finish_date = forms.DateField(label="前处理完成时间", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    # 以下4个元素为步骤1-4
    first_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True), label="步骤一",
                                                          required=False,
                                                          widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    second_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True), label="步骤二",
                                                           required=False,
                                                           widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    third_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True), label="步骤三",
                                                          required=False,
                                                          widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    fourth_operate_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True), label="步骤四",
                                                           required=False,
                                                           widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    page_person = forms.ModelMultipleChoiceField(queryset=OperatePerson.objects.filter(valid=True), label="跑胶", required=False,
                                                 widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    sample_overplus = forms.NullBooleanField(label="样本剩余",
                                             widget=forms.NullBooleanSelect(attrs={'class': 'form-control'}))
    sample_overplus_status = forms.ModelMultipleChoiceField(
        queryset=SampleStatus.objects.all(), label="剩余样本状态", required=False, widget=forms.SelectMultiple(
            attrs={'class': 'form-control'}))
    project_interrupt = forms.ModelChoiceField(queryset=ProjectInterrupt.objects.all(), label="项目中断类型",
                                               required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = SampleRecord
        fields = [
            'priority',
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
            'project_interrupt',
        ]


class TestAnalysisForm(forms.ModelForm):
    # 定义检测分析信息修改表单
    instrument_type = forms.ModelChoiceField(queryset=Machine.objects.all(), label="上机仪器",
                                             required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    date_test = forms.DateField(label="上机日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    date_searchlib = forms.DateField(label="搜库日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    date_send_report = forms.DateField(label="报告发送日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    date_send_rawdata = forms.DateField(label="原始数据发送日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    pro_deadline = forms.DateField(label="项目截止日期", widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = SampleRecord
        fields = [
            'instrument_type',
            'date_test',
            'date_searchlib',
            'date_send_report',
            'date_send_rawdata',
            'pro_deadline',
        ]
