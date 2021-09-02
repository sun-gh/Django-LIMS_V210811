from django import forms
from .models import ProjectOrder, SalePerson, PayType


class ProjectOrderForm(forms.ModelForm):
    # 定义项目结算修改表单

    project_sum = forms.DecimalField(label="项目金额", required=False, max_digits=10, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sale_person = forms.ModelChoiceField(queryset=SalePerson.objects.filter(valid=True), label="销售人员", required=False,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    pay_type = forms.ModelChoiceField(queryset=PayType.objects.all(), label="结算方式", required=False,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    # contract_record = forms.BooleanField(label="合同记录", widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectOrder
        fields = [
            'project_sum',
            # 'sale_person',
            # 'pay_type',
            'contract_record',
            'note',

        ]
