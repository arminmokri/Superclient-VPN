from django.contrib import admin
from django import forms
from .models import *
from ..action.service.Network_Util import *
from .service.country_code import *
from .service.timezone import *


class GeneralAdminForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        choices=tuple((key, key) for key in timezone()), initial="GMT"
    )

    class Meta:
        model = General
        widgets = {
            "dns": forms.Textarea,
            "check_vpn_curl_list": forms.Textarea,
            "check_vpn_ping_list": forms.Textarea,
        }
        fields = "__all__"


@admin.register(General)
class GeneralAdmin(admin.ModelAdmin):
    form = GeneralAdminForm
    list_display = ("dns_Mode", "dns", "log")

    def has_add_permission(self, request):
        base_add_permission = super(GeneralAdmin, self).has_add_permission(request)
        if base_add_permission:
            count = General.objects.all().count()
            if count == 0:
                return True
            else:
                return False

    def has_delete_permission(self, request, obj=None):
        base_delete_permission = super(GeneralAdmin, self).has_delete_permission(
            request, obj
        )
        if base_delete_permission:
            return False

    class Meta:
        model = General
        fields = "__all__"


class LanConfigAdminForm(forms.ModelForm):
    interface = forms.ChoiceField(
        choices=tuple((key, key) for key in Network_Util().get_lan_interfaces())
    )

    class Meta:
        model = LanConfig
        fields = "__all__"


@admin.register(LanConfig)
class LanConfigAdmin(admin.ModelAdmin):
    form = LanConfigAdminForm
    list_display = ("interface", "dhcp", "ip_address_1", "subnet_mask_1")


class WlanConfigAdminForm(forms.ModelForm):
    interface = forms.ChoiceField(
        choices=tuple((key, key) for key in Network_Util().get_wlan_interfaces())
    )
    country_code = forms.ChoiceField(
        choices=tuple((key, country_code()[key]) for key in country_code()),
        initial="CN",
    )

    class Meta:
        model = LanConfig
        fields = "__all__"


@admin.register(WlanConfig)
class WLanConfigAdmin(admin.ModelAdmin):
    form = WlanConfigAdminForm
    list_display = ("interface", "ssid1", "dhcp", "ip_address_1", "subnet_mask_1")


class HotspotConfigAdminForm(forms.ModelForm):
    interface = forms.ChoiceField(
        choices=tuple((key, key) for key in Network_Util().get_wlan_interfaces())
    )
    country_code = forms.ChoiceField(
        choices=tuple((key, country_code()[key]) for key in country_code()),
        initial="CN",
    )

    class Meta:
        model = HotspotConfig
        widgets = {
            "mac_address_filter_list": forms.Textarea,
        }
        fields = "__all__"


@admin.register(HotspotConfig)
class HotspotConfigAdmin(admin.ModelAdmin):
    form = HotspotConfigAdminForm
    list_display = ("interface", "channel", "ssid")

    def has_add_permission(self, request):
        base_add_permission = super(HotspotConfigAdmin, self).has_add_permission(
            request
        )
        if base_add_permission:
            count = HotspotConfig.objects.all().count()
            if count == 0:
                return True
            else:
                return False


class DhcpServerConfigAdminForm(forms.ModelForm):
    interface = forms.ChoiceField(
        choices=tuple((key, key) for key in Network_Util().get_interfaces())
    )

    class Meta:
        model = DhcpServerConfig
        fields = "__all__"


@admin.register(DhcpServerConfig)
class DhcpServerConfigAdmin(admin.ModelAdmin):
    form = DhcpServerConfigAdminForm
    list_display = (
        "interface",
        "ip_address",
        "subnet_mask",
        "dhcp_ip_address_from",
        "dhcp_ip_address_to",
    )
