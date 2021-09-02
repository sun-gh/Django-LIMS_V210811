from django import forms
from .models import ProjectContract, CutPayment
from project_order.models import ProjectOrder
from customer.models import UnitInvoice


class EditProjectContractForm(forms.ModelForm):
    # 定义编辑项目合同表单

    unit = forms.ModelChoiceField(queryset=UnitInvoice.objects.all(), label="单位",
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    linkman = forms.CharField(label="联系人", widget=forms.TextInput(attrs={'class': 'form-control'}))
    contract_file = forms.FileField(label="合同附件", required=False, widget=forms.ClearableFileInput(
        attrs={'class': 'form-control-file'}))
    callback_date = forms.DateField(label="合同回收日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectContract
        fields = [

            'project_order',
            # 'unit_name',
            'linkman',
            'contract_file',
            'callback_date',
            'creator',
            'note',
        ]


class AddProjectContractForm(EditProjectContractForm):
    # 定义添加项目合同表单
    project_order = forms.ModelMultipleChoiceField(queryset=ProjectOrder.objects.filter(contract_record=False),
                                                   label="关联项目",
                                                   widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    unit = forms.ModelChoiceField(queryset=UnitInvoice.objects.all(), label="单位", required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    linkman = forms.CharField(label="联系人", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    callback_date = None


class AdvancepayContractForm(forms.ModelForm):
    # 定义预付款合同表单
    contract_type_choice = (
        # (0, "项目合同"),
        (1, "预付款合同"),
        (2, "代开票合同"),
    )

    unit = forms.ModelChoiceField(queryset=UnitInvoice.objects.all(),
                                  label="单位", widget=forms.Select(attrs={'class': 'form-control'}))
    linkman = forms.CharField(label="联系人", widget=forms.TextInput(attrs={'class': 'form-control'}))
    contract_sum = forms.DecimalField(label="合同金额", max_digits=10, decimal_places=2,
                                      widget=forms.NumberInput(attrs={'class': 'form-control'}))
    contract_type = forms.IntegerField(label="合同类型", widget=forms.Select(choices=contract_type_choice,
                                                                         attrs={'class': 'form-control'}))
    contract_file = forms.FileField(label="合同附件", required=False, widget=forms.ClearableFileInput(
        attrs={'class': 'form-control-file'}))
    callback_date = forms.DateField(label="合同回收日期", required=False, widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectContract
        fields = [

            # 'unit_name',
            'linkman',
            'contract_sum',
            'contract_type',
            'contract_file',
            'callback_date',
            'creator',
            'note',
        ]


class CutPaymentForm(forms.ModelForm):
    # 定义预付款扣款表单
    link_contract = forms.ModelChoiceField(queryset=ProjectContract.objects.filter(contract_type=1),
                                           label="关联合同", widget=forms.Select(attrs={'class': 'form-control'}))
    cut_sum = forms.DecimalField(label="扣款金额", max_digits=10, decimal_places=2,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    link_order = forms.ModelMultipleChoiceField(queryset=ProjectOrder.objects.all(), label="关联项目",
                                                widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    applicant = forms.CharField(label="申请人", widget=forms.TextInput(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CutPayment
        fields = [
            'link_contract',
            'cut_sum',
            'link_order',
            'applicant',
            'note',

        ]
