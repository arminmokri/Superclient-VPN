from pathlib import Path

# local
from .Execte import *


class Network_Util:
    def __init__(self):
        self.interface_list = (
            Path(__file__).resolve().parent / "template_network/interface_list.sh"
        )

    def get_interfaces(self):
        return self.get_lan_interfaces() + self.get_wlan_interfaces()

    def is_interface(self, interface):
        res = True if interface in self.get_interfaces() else False
        return res

    def get_lan_interfaces(self):
        c = Execte("{} {}".format(self.interface_list, "eth"))
        c.do()
        addrs = c.stdout.strip().split("\n")
        addrs.sort()
        return addrs

    def is_lan_interface(self, interface):
        res = True if interface in self.get_lan_interfaces() else False
        return res

    def get_first_lan_interface(self):
        return self.get_lan_interfaces()[0]

    def is_lan_interface_kernel_native(self, interface):
        if "eth" in interface:
            return True
        else:
            return False

    def get_lan_interfaces_kernel_native(self):
        addrs = self.get_lan_interfaces()
        kernel_native_addrs = []
        for addr in addrs:
            if self.is_lan_interface_kernel_native(addr):
                kernel_native_addrs.append(addr)
        return kernel_native_addrs

    def get_lan_interface_kernel_native_index(self, interface):
        return int(interface.replace("eth", ""))

    def get_lan_interface_kernel_native_before_or_after(self, index):
        before = "eth" + str(index - 1)
        after = "eth" + str(index + 1)
        addrs = self.get_lan_interfaces_kernel_native()
        if before in addrs:
            return before
        elif after in addrs:
            return after
        else:
            return None

    def get_wlan_interfaces(self):
        c = Execte("{} {}".format(self.interface_list, "wlan"))
        c.do()
        addrs = c.stdout.strip().split("\n")
        addrs.sort()
        return addrs

    def is_wlan_interface(self, interface):
        res = True if interface in self.get_wlan_interfaces() else False
        return res

    def get_first_wlan_interface(self):
        return self.get_wlan_interfaces()[0]

    def is_wlan_interface_kernel_native(self, interface):
        if "wlan" in interface:
            return True
        else:
            return False

    def get_wlan_interfaces_kernel_native(self):
        addrs = self.get_wlan_interfaces()
        kernel_native_addrs = []
        for addr in addrs:
            if self.is_wlan_interface_kernel_native(addr):
                kernel_native_addrs.append(addr)
        return kernel_native_addrs

    def get_wlan_interface_kernel_native_index(self, interface):
        return int(interface.replace("wlan", ""))

    def get_wlan_interface_kernel_native_before_or_after(self, index):
        before = "wlan" + str(index - 1)
        after = "wlan" + str(index + 1)
        addrs = self.get_wlan_interfaces_kernel_native()
        if before in addrs:
            return before
        elif after in addrs:
            return after
        else:
            return None

    def get_mac(self, interface):
        if self.is_interface(interface):
            return self._get_mac(interface)
        else:
            return None

    def _get_mac(self, interface):
        f = open("/sys/class/net/" + interface + "/address", "r")
        return f.read().strip()

    def get_interface_by_mac(self, mac):
        addrs = self.get_interfaces()
        for addr in addrs:
            if mac == self._get_mac(addr):
                return addr
        return None
