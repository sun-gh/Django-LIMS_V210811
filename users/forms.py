from django import forms
from django.contrib.contenttypes.models import ContentType


class PermissionForm(forms.Form):
    # 定义权限添加

    model_name = forms.ModelChoiceField(queryset=ContentType.objects.all(), label="模型",
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    permission_name = forms.CharField(label="权限名称", widget=forms.TextInput(attrs={'class': 'form-control'}))
    permission_describe = forms.CharField(label="权限描述", widget=forms.TextInput(attrs={'class': 'form-control'}))
