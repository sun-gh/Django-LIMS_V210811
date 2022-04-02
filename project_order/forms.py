from django import forms
from .models import ProjectOrder, SalePerson, PayType


class ProjectOrderForm(forms.ModelForm):
    # 定义项目结算修改表单
    project_source = forms.IntegerField(label="项目来源", widget=forms.Select(  # required=False,
        choices=ProjectOrder.project_source_choice, attrs={'class': 'form-control'}))
    customer_source = forms.IntegerField(label="客户来源", widget=forms.Select(
        choices=(('', '--------'),)+ProjectOrder.customer_source_choice, attrs={'class': 'form-control'}))
    project_sum = forms.DecimalField(label="项目金额", required=False, max_digits=10, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))

    pay_type = forms.ModelChoiceField(queryset=PayType.objects.all(), label="结算方式", required=False,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectOrder
        fields = [
            'project_source',
            'customer_source',
            'project_sum',
            'contract_record',
            'note',

        ]
