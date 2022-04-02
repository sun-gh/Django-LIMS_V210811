from django import forms
from .models import ClinicIntention, SampleType, DemandType, FollowUpRecord
from customer.models import UnitInvoice


class IntentionForm(forms.ModelForm):
    # 定义临床意向表单
    customer_name = forms.CharField(label="客户姓名", widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_info = forms.CharField(label="联系方式", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    unit = forms.ModelChoiceField(queryset=UnitInvoice.objects.all(), label="单位",
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.CharField(label="科室/院系", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    leading_official = forms.CharField(label="负责人", required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control'}))
    disease_type = forms.CharField(label="疾病种类", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    plan_needed = forms.NullBooleanField(label="是否需方案设计", widget=forms.NullBooleanSelect(attrs={'class': 'form-control'}))
    plan_type = forms.IntegerField(label="方案类型", required=False, widget=forms.Select(
        choices=ClinicIntention.plan_choice, attrs={'class': 'form-control'}))
    plan_deadline = forms.DateField(label="方案截止日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    customer_budget = forms.DecimalField(label="客户预算", max_digits=10, decimal_places=2, required=False,
                                         widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sample_number = forms.IntegerField(label="计划样本数", required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    collect_time = forms.DateField(label="计划收样日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    send_time = forms.DateField(label="计划送样日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    sample_type = forms.ModelChoiceField(queryset=SampleType.objects.all(), label="样本类型", required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    project_stage = forms.IntegerField(label="项目阶段", required=False, widget=forms.Select(
        choices=ClinicIntention.project_stage_choice, attrs={'class': 'form-control'}))
    demand_estimate = forms.ModelMultipleChoiceField(queryset=DemandType.objects.all(), label="需求预估", required=False,
                                                     widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ClinicIntention
        fields = [
            'customer_name',
            'contact_info',
            'unit',
            'department',
            'leading_official',
            'disease_type',
            'plan_needed',
            'plan_type',
            'plan_deadline',
            'customer_budget',
            'sample_number',
            'collect_time',
            'send_time',
            'sample_type',
            'project_stage',
            'demand_estimate',
            'note',
            'add_person',
        ]


class FollowUpRecordForm(forms.ModelForm):
    # 定义跟进记录表单
    communicate_time = forms.DateField(label="沟通时间", widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm'}))
    linkman = forms.CharField(label="对接人", widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                                         'placeholder': '对接人'}))
    communicate_content = forms.CharField(label="沟通内容", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '3', 'placeholder': '沟通内容'}))
    recorder = forms.CharField(label="记录人", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = FollowUpRecord
        fields = [
            'communicate_time',
            'linkman',
            'communicate_content',
            'recorder',
            ]


class IntentionSearchForm(forms.Form):
    # 定义意向查询表单
    plan_needed = forms.NullBooleanField(label="需要方案", widget=forms.NullBooleanSelect(
        attrs={'class': 'form-control form-control-sm'}))
    plan_type = forms.IntegerField(label="方案类型", required=False, widget=forms.Select(
        choices=ClinicIntention.plan_choice, attrs={'class': 'form-control form-control-sm'}))
    project_stage = forms.IntegerField(label="项目阶段", required=False, widget=forms.Select(
        choices=ClinicIntention.project_stage_choice, attrs={'class': 'form-control form-control-sm'}))
