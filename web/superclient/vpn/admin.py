from django.contrib import admin
from django import forms
from .models import OpenVpnConfig, OpenconnectConfig, V2rayConfig
from ..action.models import ServiceStatus


class OpenconnectConfigAdminForm(forms.ModelForm):
    class Meta:
        model = OpenconnectConfig
        widgets = {
            "last_log": forms.Textarea,
        }
        fields = "__all__"


@admin.register(OpenconnectConfig)
class OpenconnectConfigAdmin(admin.ModelAdmin):
    form = OpenconnectConfigAdminForm
    list_display = ["name", "subscription", "enable", "priority", "success", "failed"]
    readonly_fields = ["last_log"]
    exclude = ["subscription"]

    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        configuration_list = [
            "name",
            "description",
            "enable",
            "priority",
            "success",
            "failed",
            "last_log",
        ]
        for i in range(len(configuration_list)):
            fields.remove(configuration_list[i])
            fields.insert(i, configuration_list[i])
        return fields


class OpenVpnConfigAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OpenVpnConfig
        widgets = {
            "last_log": forms.Textarea,
        }
        fields = "__all__"


@admin.register(OpenVpnConfig)
class OpenVpnConfigAdmin(admin.ModelAdmin):
    form = OpenVpnConfigAdminForm
    list_display = ("name", "subscription", "enable", "priority", "success", "failed")
    readonly_fields = ["last_log", "ovpn"]
    exclude = ["subscription"]

    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        configuration_list = [
            "name",
            "description",
            "enable",
            "priority",
            "success",
            "failed",
            "last_log",
        ]
        for i in range(len(configuration_list)):
            fields.remove(configuration_list[i])
            fields.insert(i, configuration_list[i])
        return fields


class V2rayConfigAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = V2rayConfig
        widgets = {
            "last_log": forms.Textarea,
            "config_json": forms.Textarea,
            "config_url": forms.Textarea,
        }
        fields = "__all__"


@admin.register(V2rayConfig)
class V2rayConfigAdmin(admin.ModelAdmin):
    form = V2rayConfigAdminForm
    list_display = [
        "name",
        "subscription",
        "enable",
        "priority",
        "success",
        "failed",
        "protocol",
        "config_url",
    ]
    readonly_fields = ["last_log", "protocol", "config_json", "hostname"]
    exclude = ["subscription"]

    def get_fields(self, request, obj=None, **kwargs):
        fields = super().get_fields(request, obj, **kwargs)
        configuration_list = [
            "name",
            "description",
            "enable",
            "priority",
            "success",
            "failed",
            "last_log",
        ]
        for i in range(len(configuration_list)):
            fields.remove(configuration_list[i])
            fields.insert(i, configuration_list[i])
        return fields

    def save_model(self, request, obj, form, change):
        V2rayConfig.bulkadd(obj.config_url)
