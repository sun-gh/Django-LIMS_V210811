from django import forms
from .models import ApplyInvoice, InvoiceRequire, InvoiceInfo, VoidRedInfo
from contract_manage.models import ProjectContract
from customer.models import UnitInvoice


class ApplyInvoiceForm(forms.ModelForm):
    # 定义申请开票表单
    related_contract = forms.ModelChoiceField(queryset=ProjectContract.objects.all(), label="关联合同",
                                              widget=forms.Select(attrs={'class': 'form-control'}))
    unit_name = forms.ModelChoiceField(queryset=UnitInvoice.objects.all(),
                                       label="开票单位", widget=forms.Select(attrs={'class': 'form-control'}))
    invoice_sum = forms.DecimalField(label="开票金额", max_digits=10, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sheet_num = forms.IntegerField(label="开票张数", max_value=10,
                                   widget=forms.NumberInput(attrs={'class': 'form-control'}))
    invoice_require = forms.ModelMultipleChoiceField(queryset=InvoiceRequire.objects.all(), label="开票要求",
                                                     required=False,
                                                     widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    file_input = forms.FileField(label="报账文件", required=False, widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'class': 'form-control-file'}))
    invoice_type = forms.IntegerField(label="开票类型", widget=forms.Select(
        choices=ApplyInvoice.invoice_type_choice, attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    linkman = forms.CharField(label="联系人", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.IntegerField(label="电话", required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    address_linkman = forms.CharField(label="收件地址", required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))
    applicant = forms.CharField(label="申请人", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ApplyInvoice
        fields = [
            'related_contract',
            # 'unit',
            'invoice_sum',
            'sheet_num',
            'invoice_require',
            # 文件要单独处理
            'reimburse_file',
            'invoice_type',
            'note',
            'linkman',
            'phone',
            'address_linkman',
            'applicant',
        ]


class FileApplyInvoiceForm(forms.ModelForm):
    # 定义归档申请开票表单

    post_date = forms.DateField(label="邮寄日期", widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    express_num = forms.CharField(label="快递单号", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ApplyInvoice
        fields = [
            'post_date',
            'express_num',
        ]


class EditInvoiceInfoForm(forms.ModelForm):
    # 定义修改发票信息表单

    invoice_num = forms.IntegerField(label="发票号", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    invoice_sum = forms.DecimalField(label="发票金额", max_digits=10, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    invoice_date = forms.DateField(label="开票日期", widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    invoice_callback = forms.NullBooleanField(label="发票是否收回",
                                              widget=forms.NullBooleanSelect(attrs={'class': 'form-control'}))
    reason = forms.CharField(label="未收回原因", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = InvoiceInfo
        fields = [
            'invoice_num',
            'invoice_sum',
            'invoice_date',
            'invoice_callback',
            'reason',
        ]


class EditPayInfoForm(forms.ModelForm):
    # 定义修改回款信息表单

    payment_date = forms.DateField(label="回款日期", widget=forms.DateInput(
        format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}))
    payment_sum = forms.DecimalField(label="回款金额", max_digits=10, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    note = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = InvoiceInfo
        fields = [
            'payment_date',
            'payment_sum',
            'note',
        ]


class ApplyVoidRedForm(forms.ModelForm):
    # 定义申请发票冲红

    link_invoice = forms.ModelMultipleChoiceField(queryset=InvoiceInfo.objects.filter(void_red=0), label="原发票号",
                                                  widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    treat_type = forms.IntegerField(label="处理类型", widget=forms.Select(
        choices=VoidRedInfo.treat_choice, attrs={'class': 'form-control'}))
    reason = forms.CharField(label="作废/冲红原因", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    applicant = forms.CharField(label="申请人", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = InvoiceInfo
        fields = [
            'link_invoice',
            'treat_type',
            'reason',
            'applicant',
        ]
