from django import forms
from .models import UnitInvoice, CustomerInfo


class UnitForm(forms.ModelForm):
    # 定义客户单位表单

    unit_name = forms.CharField(label="单位名称", widget=forms.TextInput(attrs={'placeholder': '请输入单位全称！',
                                                                            'class': 'form-control'}))
    duty_paragraph = forms.CharField(label="税号", required=False,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    bank = forms.CharField(label="开户行", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), )
    account = forms.CharField(label="银行账号", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label="单位地址", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="联系电话", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    person_add = forms.CharField(label="添加人", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UnitInvoice
        fields = ['unit_name',
                  'duty_paragraph',
                  'bank',
                  'account',
                  'address',
                  'phone',
                  'person_add',

                  ]


class CustomerInfoForm(forms.ModelForm):
    # 定义客户信息表单
    customer_name = forms.CharField(label="客户姓名", widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="电话", required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    mail = forms.EmailField(label="邮箱", required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    unit = forms.ModelChoiceField(queryset=UnitInvoice.objects.all(), label="单位", required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.CharField(label="科室/院系", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    leading_official = forms.CharField(label="负责人", required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    person_add = forms.CharField(label="添加人", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomerInfo
        fields = [
            'customer_name',
            'phone',
            'mail',
            'unit',
            'department',
            'leading_official',
            'note',
            'person_add',
            ]
