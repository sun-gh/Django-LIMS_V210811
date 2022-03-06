from django import forms
from .models import DemandCollect, DemandDesign


class EditDemandForm(forms.ModelForm):
    # 定义编辑需求表单
    demand_type = forms.IntegerField(label="需求类型", widget=forms.Select(choices=DemandCollect.demand_type_choices,
                                                                       attrs={'class': 'form-control'}))
    demand_describe = forms.CharField(label="需求描述", widget=forms.Textarea(attrs={'rows': '3', 'class': 'form-control'}))
    urgent_degree = forms.IntegerField(label="紧急程度", widget=forms.Select(choices=DemandCollect.urgent_levels,
                                                                         attrs={'class': 'form-control'}))
    important_degree = forms.IntegerField(label="重要程度", widget=forms.Select(choices=DemandCollect.important_levels,
                                                                            attrs={'class': 'form-control'}))
    file = forms.ImageField(label="相关截图", required=False, widget=forms.ClearableFileInput(
        attrs={'class': 'form-control-file'}))

    class Meta:
        model = DemandCollect
        fields = ['demand_type',
                  'demand_describe',
                  'urgent_degree',
                  'important_degree',
                  'file',
                  # 'note',
                  'sponsor',
                  ]


class VerifyDemand(forms.ModelForm):
    # 定义需求审核表单
    verify_result = forms.IntegerField(label="审核结果", min_value=1,
                                       widget=forms.Select(choices=DemandCollect.verify_result_choices,
                                                           attrs={'class': 'form-control'}))
    note = forms.CharField(label="审核建议", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DemandCollect
        fields = [
                  'verify_result',
                  'note',
                  ]


class EstimateDemandForm(forms.ModelForm):
    # 定义需求评估表单
    estimate_result = forms.IntegerField(label="评估结果", min_value=1,
                                         widget=forms.Select(choices=DemandDesign.estimate_result_choices,
                                                             attrs={'class': 'form-control'}))
    note = forms.CharField(label="评估建议", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    predict_cycle = forms.DecimalField(label="预计开发周期", max_digits=4, decimal_places=1, required=False,
                                       widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DemandDesign
        fields = [
            'estimate_result',
            'note',
            'predict_cycle',
          ]


class DesignEditForm(forms.ModelForm):
    # 定义需求设计开始和完成时间修改表单
    start_time = forms.DateField(label="开始时间", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    finish_time = forms.DateField(label="完成时间", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = DemandDesign
        fields = [
            'start_time',
            'finish_time',
          ]


class DemandSearchForm(forms.Form):
    # 定义需求反馈页的搜索表单
    status_choices = (
        (0, "--------"),
        (1, "待审核"),
        (2, "已审核"),
        (3, "已退回"),
    )
    status = forms.IntegerField(label="状态",
                                widget=forms.Select(choices=status_choices,
                                                    attrs={'class': 'form-control form-control-sm'}))
    sponsor = forms.CharField(label="提出人", required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    demand_describe = forms.CharField(label="需求描述", required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))


class DesignSearchForm(forms.Form):
    # 定义需求设计页的搜索表单
    status_choices = (
        (0, "--------"),
        (1, "待评估"),
        (2, "关闭"),
        (3, "待开发"),
        (4, "开发中"),
        (5, "已完成"),
    )
    status = forms.IntegerField(label="状态",
                                widget=forms.Select(choices=status_choices,
                                                    attrs={'class': 'form-control form-control-sm'}))
    sponsor = forms.CharField(label="提出人", required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    demand_describe = forms.CharField(label="需求描述", required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
