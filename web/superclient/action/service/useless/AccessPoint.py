import logging
import shutil
import psutil
import time
from pathlib import Path

### local
from .ConfigItem import *
from .Execte import *
from ...setting.models import Setting


class AccessPoint:
    def __init__(
        self,
        interface,
        channel,
        ssid,
        wpa_passphrase,
        ip,
        dhcp_ip_from,
        dhcp_ip_to,
        netmask,
        setting: Setting,
    ):
        # hostapd configs
        self.interface = ConfigItem("interface", interface)
        self.channel = ConfigItem("channel", channel)
        self.ssid = ConfigItem("ssid", ssid)
        self.wpa_passphrase = ConfigItem("wpa_passphrase", wpa_passphrase)
        self.driver = ConfigItem("driver", "nl80211")
        self.hw_mode = ConfigItem("hw_mode", "g")
        self.macaddr_acl = ConfigItem("macaddr_acl", "0")
        self.auth_algs = ConfigItem("auth_algs", "1")
        self.ignore_broadcast_ssid = ConfigItem("ignore_broadcast_ssid", "0")
        self.wpa = ConfigItem("wpa", "2")
        self.wpa_key_mgmt = ConfigItem("wpa_key_mgmt", "WPA-PSK")
        self.wpa_pairwise = ConfigItem("wpa_pairwise", "TKIP")
        self.rsn_pairwise = ConfigItem("rsn_pairwise", "CCMP")
        self.hostapd_config_path = Path(__file__).resolve().parent / "hostapd.conf"
        # interface ip
        self.ip = ip
        # dnsmasq
        self.dhcp_ip_from = dhcp_ip_from
        self.dhcp_ip_to = dhcp_ip_to
        self.netmask = netmask
        self.setting = setting
        self.lease_time = "24h"
        self.dnsmasq_log_path = "/tmp/dnsmasq.log"
        self.dnsmasq_leases_path = "/tmp/dnsmasq.leases"

    def _check_dependencies(self):
        check = True

        if shutil.which("ifconfig") is None:
            logging.error(
                "hostapd executable not found. Make sure you have installed ifconfig."
            )
            check = False

        if shutil.which("hostapd") is None:
            logging.error(
                "hostapd executable not found. Make sure you have installed hostapd."
            )
            check = False

        if shutil.which("dnsmasq") is None:
            logging.error(
                "dnsmasq executable not found. Make sure you have installed dnsmasq."
            )
            check = False

        return check

    def is_running(self):
        proceses = [proc.name() for proc in psutil.process_iter()]
        return "hostapd" in proceses or "dnsmasq" in proceses

    def _write_hostapd_config(self):
        config = (
            self.interface.toString()
            + self.ssid.toString()
            + self.wpa_passphrase.toString()
            + self.driver.toString()
            + self.hw_mode.toString()
            + self.channel.toString()
            + self.macaddr_acl.toString()
            + self.auth_algs.toString()
            + self.ignore_broadcast_ssid.toString()
            + self.wpa.toString()
            + self.wpa_key_mgmt.toString()
            + self.wpa_pairwise.toString()
            + self.rsn_pairwise.toString()
        )
        with open(self.hostapd_config_path, "w") as hostapd_config_file:
            hostapd_config_file.write(config)

        logging.debug("hostapd config created to '%s'.", self.hostapd_config_path)

    def start(self):
        if not self._check_dependencies():
            return False

        if self.is_running():
            logging.debug("already started.")
            return True

        self._write_hostapd_config()

        try:
            logging.debug("stoping wpa_supplicant.")
            c1 = Execte("killall wpa_supplicant", False)
            c1.do()
            c1.print()

            logging.debug("turning off radio wifi.")
            c2 = Execte("nmcli radio wifi off", False)
            c2.do()
            c2.print()

            logging.debug("unblocking wlan.")
            c3 = Execte("rfkill unblock wlan", False)
            c3.do()
            c3.print()

            logging.debug("waiting 1 sec.")
            time.sleep(1)

        except:
            pass

        logging.debug(
            "interface: {} on IP: {} is up.".format(self.interface.value, self.ip)
        )
        c4 = Execte(
            "ifconfig {} up {} netmask {}".format(
                self.interface.value, self.ip, self.netmask
            ),
            False,
        )
        c4.do()
        c4.print()

        logging.debug("waiting 2 sec.")
        time.sleep(2)

        dns = ""
        if self.setting.dns_Mode == self.setting.DnsMode._3 and self.setting.dns != "":
            dns_list = self.setting.dns.split(",")
            for i in range(len(dns_list)):
                dns_list[i] = "/#/" + dns_list[i]
            dns = "--address=" + ",".join(dns_list)

        logging.debug("delete last dnsmasq log.")
        c5 = Execte("rm {}".format(self.dnsmasq_log_path), False)
        c5.do()
        c5.print()

        logging.debug("running dnsmasq.")
        c6 = Execte(
            "dnsmasq --dhcp-authoritative --no-negcache --strict-order --clear-on-reload --log-queries --log-dhcp --interface={} --listen-address={} --dhcp-range={},{},{},{} --log-facility={} --dhcp-leasefile={} {}".format(
                self.interface.value,
                self.ip,
                self.dhcp_ip_from,
                self.dhcp_ip_to,
                self.netmask,
                self.lease_time,
                self.dnsmasq_log_path,
                self.dnsmasq_leases_path,
                dns,
            ),
            False,
        )
        c6.do()
        c6.print()

        logging.debug("waiting 2 sec.")
        time.sleep(2)

        logging.debug("running hostapd.")
        c7 = Execte("hostapd -B {}".format(self.hostapd_config_path), False)
        c7.do()
        c7.print()

        logging.debug("hotspot is running.")

        return True

    def stop(self):

        if not self.is_running():
            logging.debug("not running.")
            return True

        # bring down the interface
        logging.debug("interface {} is down.".format(self.interface.value))
        c1 = Execte("ifconfig {} down".format(self.interface.value), False)
        c1.do()
        c1.print()

        # stop hostapd
        logging.debug("stopping hostapd.")
        c2 = Execte("pkill hostapd", False)
        c2.do()
        c2.print()

        # stop dnsmasq
        logging.debug("stopping dnsmasq.")
        c3 = Execte("killall dnsmasq", False)
        c3.do()
        c3.print()

        logging.debug("hotspot has stopped.")
        return True

    def restart(self):
        self.stop()
        time.sleep(2)
        self.start()
