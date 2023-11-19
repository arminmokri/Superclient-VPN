from django.contrib import admin
from django import forms
from .models import VitaminConfig


class VitaminConfigAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = VitaminConfig
        widgets = {
            "serverlist_json": forms.Textarea,
        }
        fields = "__all__"


@admin.register(VitaminConfig)
class VitaminConfigAdmin(admin.ModelAdmin):
    form = VitaminConfigAdminForm
    list_display = ["username", "password", "resync", "openvpn", "anyconnect", "v2ray"]
