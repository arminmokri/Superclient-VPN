from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..action.service.Network_Util import Network_Util

# Create your models here.
class General(models.Model):
    class VpnSmartMode(models.TextChoices):
        success_chance = "success_chance", "Success Chance"
        priority = "priority", "Priority"
        circular = "circular", "Circular"

    vpn_smart_mode = models.CharField(
        max_length=64, choices=VpnSmartMode.choices, default=VpnSmartMode.success_chance
    )
    timezone = models.CharField(max_length=128, default="GMT")

    class DefaultGatewayMode(models.TextChoices):
        dhcp = "dhcp", "Dhcp"
        manual = "manual", "Manual"

    default_gateway_mode = models.CharField(
        max_length=16,
        choices=DefaultGatewayMode.choices,
        default=DefaultGatewayMode.dhcp,
    )
    default_gateway = models.CharField(max_length=16, blank=True)

    class DnsMode(models.TextChoices):
        _1 = "1", "Do Nothing"
        _2 = "2", "Handle in system"
        _3 = "3", "Handle with socks (only for v2ray)"

    dns_Mode = models.CharField(
        max_length=8, choices=DnsMode.choices, default=DnsMode._2
    )
    dns = models.CharField(
        max_length=128, default="8.8.8.8\n1.1.1.1\n208.67.222.222", blank=True
    )
    log = models.BooleanField(default=False)
    number_of_try_for_each_vpn = models.IntegerField(default=3)
    timeout_of_try_for_each_vpn = models.IntegerField(default=20)

    class CheckVpnMethod(models.TextChoices):
        disable = "disable", "Disable"
        curl = "curl", "Curl"
        ping = "ping", "Ping"
        random = "random", "Curl or Ping randomly"

    check_vpn_method = models.CharField(
        max_length=64, choices=CheckVpnMethod.choices, default=CheckVpnMethod.random
    )

    class CheckVpnListMethod(models.TextChoices):
        one = "one", "One from one of the list successful"
        two = "two", "One from two of the list successful"
        three = "three", "One from three of the list successful"
        all = "all", "One from all of the list successful"
        strict = "strict", "All from all of the list successful"

    check_vpn_list_method = models.CharField(
        max_length=64,
        choices=CheckVpnListMethod.choices,
        default=CheckVpnListMethod.three,
    )
    check_vpn_curl_list = models.CharField(
        max_length=4098,
        default="https://api.ipify.org?format=json\nhttp://api.ipify.org?format=json\nhttps://checkip.amazonaws.com\nhttp://checkip.amazonaws.com\nhttps://icanhazip.com\nhttp://icanhazip.com\nhttps://jsonip.com",
        blank=True,
    )
    check_vpn_curl_timeout = models.IntegerField(default=15)
    check_vpn_curl_retry = models.IntegerField(default=1)
    check_vpn_ping_list = models.CharField(
        max_length=4098, default="8.8.8.8\n1.1.1.1\n208.67.222.222", blank=True
    )
    check_vpn_ping_timeout = models.IntegerField(default=5)
    check_vpn_ping_retry = models.IntegerField(default=3)

    class V2rayMode(models.TextChoices):
        badvpn_tun2socks = "badvpn-tun2socks", "badvpn-tun2socks"
        go_tun2socks = "go-tun2socks", "go-tun2socks"
        tun2socks = "tun2socks", "tun2socks"

    v2ray_mode = models.CharField(
        max_length=64, choices=V2rayMode.choices, default=V2rayMode.badvpn_tun2socks
    )

    def save(self, *args, **kwargs):
        # self.dns = "".join(self.dns.split())
        super(General, self).save(*args, **kwargs)


def LanConfig_validate_interface(value):
    if DhcpServerConfig.objects.filter(interface=value).count() != 0:
        raise ValidationError(
            _("Network interface '%s' already exists in 'Dhcp server configs'."),
            params=(value),
        )


class LanConfig(models.Model):
    enable = models.BooleanField(default=True)
    interface = models.CharField(
        max_length=16, unique=True, validators=[LanConfig_validate_interface]
    )
    mac = models.CharField(max_length=64, default="", editable=False)
    dhcp = models.BooleanField(default=True)
    dhcp_set_default_gateway = models.BooleanField(default=True)
    ip_address_1 = models.CharField(max_length=16, blank=True)
    subnet_mask_1 = models.CharField(max_length=16, blank=True)
    ip_address_2 = models.CharField(max_length=16, blank=True)
    subnet_mask_2 = models.CharField(max_length=16, blank=True)
    ip_address_3 = models.CharField(max_length=16, blank=True)
    subnet_mask_3 = models.CharField(max_length=16, blank=True)
    ip_address_4 = models.CharField(max_length=16, blank=True)
    subnet_mask_4 = models.CharField(max_length=16, blank=True)

    @property
    def interface_mac(self):

        nu = Network_Util()
        is_interface = nu.is_interface(self.interface)
        mac = nu.get_mac(self.interface)
        interface = nu.get_interface_by_mac(self.mac)

        if is_interface and mac == self.mac:  # name and mac are ok
            return self.interface
        elif not is_interface and interface != None:  # name changed but mac is ok
            return interface
        elif (
            is_interface and mac != self.mac
        ):  # name is ok but mac is changed - like wlan0 in orangepi zero change in evrey reboot
            return self.interface
        else:  # name and mac are changed - like orangepi zero wlan0 change to wlan1 when other usb wlan is pluged
            if (
                nu.is_lan_interface_kernel_native(self.interface)
                and self.interface not in nu.get_lan_interfaces_kernel_native()
            ):
                index = nu.get_lan_interface_kernel_native_index(self.interface)
                return nu.get_lan_interface_kernel_native_before_or_after(index)
            else:
                return None

    def save(self, *args, **kwargs):
        self.mac = Network_Util().get_mac(self.interface)
        super(LanConfig, self).save(*args, **kwargs)


def WlanConfig_validate_interface(value):
    if HotspotConfig.objects.filter(interface=value).count() != 0:
        raise ValidationError(
            _("Network interface '%s' already exists in 'Hotspot configs'."),
            params=(value),
        )
    elif DhcpServerConfig.objects.filter(interface=value).count() != 0:
        raise ValidationError(
            _("Network interface '%s' already exists in 'Dhcp server configs'."),
            params=(value),
        )


class WlanConfig(models.Model):
    enable = models.BooleanField(default=True)
    interface = models.CharField(
        max_length=16, unique=True, validators=[WlanConfig_validate_interface]
    )
    mac = models.CharField(max_length=64, default="", editable=False)
    ssid1 = models.CharField(max_length=128)
    wpa_passphrase1 = models.CharField(max_length=128, blank=True)
    ssid2 = models.CharField(max_length=128, blank=True)
    wpa_passphrase2 = models.CharField(max_length=128, blank=True)
    ssid3 = models.CharField(max_length=128, blank=True)
    wpa_passphrase3 = models.CharField(max_length=128, blank=True)
    ssid4 = models.CharField(max_length=128, blank=True)
    wpa_passphrase4 = models.CharField(max_length=128, blank=True)
    country_code = models.CharField(max_length=8, default="CN")

    class Driver(models.TextChoices):
        nl80211 = "nl80211", "nl80211"
        wext = "wext", "wext"
        all = "nl80211,wext", "nl80211,wext"

    driver = models.CharField(
        max_length=128, choices=Driver.choices, default=Driver.all
    )
    dhcp = models.BooleanField(default=True)
    dhcp_set_default_gateway = models.BooleanField(default=True)
    ip_address_1 = models.CharField(max_length=16, blank=True)
    subnet_mask_1 = models.CharField(max_length=16, blank=True)
    ip_address_2 = models.CharField(max_length=16, blank=True)
    subnet_mask_2 = models.CharField(max_length=16, blank=True)
    ip_address_3 = models.CharField(max_length=16, blank=True)
    subnet_mask_3 = models.CharField(max_length=16, blank=True)
    ip_address_4 = models.CharField(max_length=16, blank=True)
    subnet_mask_4 = models.CharField(max_length=16, blank=True)

    @property
    def interface_mac(self):

        nu = Network_Util()
        is_interface = nu.is_interface(self.interface)
        mac = nu.get_mac(self.interface)
        interface = nu.get_interface_by_mac(self.mac)

        if is_interface and mac == self.mac:  # name and mac are ok
            return self.interface
        elif not is_interface and interface != None:  # name changed but mac is ok
            return interface
        elif (
            is_interface and mac != self.mac
        ):  # name is ok but mac is changed - like wlan0 in orangepi zero change in evrey reboot
            return self.interface
        else:  # name and mac are changed - like orangepi zero wlan0 change to wlan1 when other usb wlan is pluged
            if (
                nu.is_wlan_interface_kernel_native(self.interface)
                and self.interface not in nu.get_wlan_interfaces_kernel_native()
            ):
                index = nu.get_wlan_interface_kernel_native_index(self.interface)
                return nu.get_wlan_interface_kernel_native_before_or_after(index)
            else:
                return None

    def save(self, *args, **kwargs):
        self.mac = Network_Util().get_mac(self.interface)
        super(WlanConfig, self).save(*args, **kwargs)


def HotspotConfig_validate_interface(value):
    if WlanConfig.objects.filter(interface=value).count() != 0:
        raise ValidationError(
            _("Network interface '%s' already exists in 'Wlan configs'."),
            params=(value),
        )


class HotspotConfig(models.Model):
    enable = models.BooleanField(default=True)
    interface = models.CharField(
        max_length=16, unique=True, validators=[HotspotConfig_validate_interface]
    )
    mac = models.CharField(max_length=64, default="", editable=False)
    ssid = models.CharField(max_length=128)
    wpa_passphrase = models.CharField(max_length=128, blank=True)

    class Channel(models.TextChoices):
        _1 = "1", "1"
        _2 = "2", "2"
        _3 = "3", "3"
        _4 = "4", "4"
        _5 = "5", "5"
        _6 = "6", "6"
        _7 = "7", "7"
        _8 = "8", "8"
        _9 = "9", "9"
        _10 = "10", "10"
        _11 = "11", "11"
        _12 = "12", "12"
        _13 = "13", "13"
        _14 = "14", "14"

    channel = models.CharField(
        max_length=8, choices=Channel.choices, default=Channel._6
    )
    country_code = models.CharField(max_length=8, default="CN")

    class MAC_Address_Filter_Mode(models.TextChoices):
        disable = "disable", "Disable"
        block = "block", "Block"
        allow = "accept", "Allow"

    mac_address_filter_mode = models.CharField(
        max_length=32,
        choices=MAC_Address_Filter_Mode.choices,
        default=MAC_Address_Filter_Mode.disable,
    )
    mac_address_filter_list = models.CharField(max_length=4098, blank=True)

    @property
    def interface_mac(self):

        nu = Network_Util()
        is_interface = nu.is_interface(self.interface)
        mac = nu.get_mac(self.interface)
        interface = nu.get_interface_by_mac(self.mac)

        if is_interface and mac == self.mac:  # name and mac are ok
            return self.interface
        elif not is_interface and interface != None:  # name changed but mac is ok
            return interface
        elif (
            is_interface and mac != self.mac
        ):  # name is ok but mac is changed - like wlan0 in orangepi zero change in evrey reboot
            return self.interface
        else:  # name and mac are changed - like orangepi zero wlan0 change to wlan1 when other usb wlan is pluged
            if (
                nu.is_wlan_interface_kernel_native(self.interface)
                and self.interface not in nu.get_wlan_interfaces_kernel_native()
            ):
                index = nu.get_wlan_interface_kernel_native_index(self.interface)
                return nu.get_wlan_interface_kernel_native_before_or_after(index)
            else:
                return None

    def save(self, *args, **kwargs):
        self.mac = Network_Util().get_mac(self.interface)
        super(HotspotConfig, self).save(*args, **kwargs)


def DhcpServerConfig_validate_interface(value):
    if LanConfig.objects.filter(interface=value).count() != 0:
        raise ValidationError(
            _("Network interface '%s' already exists in 'Lan configs'."),
            params=(value),
        )
    elif WlanConfig.objects.filter(interface=value).count() != 0:
        raise ValidationError(
            _("Network interface '%s' already exists in 'Wlan configs'."),
            params=(value),
        )


class DhcpServerConfig(models.Model):
    enable = models.BooleanField(default=True)

    class DhcpModule(models.TextChoices):
        dnsmasq = "dnsmasq", "dnsmasq"
        dhcpd = "isc-dhcp-server", "isc-dhcp-server"

    dhcp_module = models.CharField(
        max_length=32, choices=DhcpModule.choices, default=DhcpModule.dnsmasq
    )
    bridge = models.BooleanField(default=True)
    interface = models.CharField(
        max_length=16, unique=True, validators=[DhcpServerConfig_validate_interface]
    )
    mac = models.CharField(max_length=64, default="", editable=False)
    ip_address = models.CharField(max_length=16, default="192.168.10.1")
    subnet_mask = models.CharField(max_length=16, default="255.255.255.0")
    dhcp_ip_address_from = models.CharField(max_length=16, default="192.168.10.10")
    dhcp_ip_address_to = models.CharField(max_length=16, default="192.168.10.30")

    @property
    def interface_mac(self):

        nu = Network_Util()
        is_interface = nu.is_interface(self.interface)
        mac = nu.get_mac(self.interface)
        interface = nu.get_interface_by_mac(self.mac)

        if is_interface and mac == self.mac:  # name and mac are ok
            return self.interface
        elif not is_interface and interface != None:  # name changed but mac is ok
            return interface
        elif (
            is_interface and mac != self.mac
        ):  # name is ok but mac is changed - like wlan0 in orangepi zero change in evrey reboot
            return self.interface
        else:  # name and mac are changed - like orangepi zero wlan0 change to wlan1 when other usb wlan is pluged
            if (
                nu.is_lan_interface_kernel_native(self.interface)
                and self.interface not in nu.get_lan_interfaces_kernel_native()
            ):
                index = nu.get_lan_interface_kernel_native_index(self.interface)
                return nu.get_lan_interface_kernel_native_before_or_after(index)
            elif (
                nu.is_wlan_interface_kernel_native(self.interface)
                and self.interface not in nu.get_wlan_interfaces_kernel_native()
            ):
                index = nu.get_wlan_interface_kernel_native_index(self.interface)
                return nu.get_wlan_interface_kernel_native_before_or_after(index)
            else:
                return None

    def save(self, *args, **kwargs):
        self.mac = Network_Util().get_mac(self.interface)
        super(DhcpServerConfig, self).save(*args, **kwargs)
