from pathlib import Path
import os
import json
import random
import time

# local
from .Execte import *
from .Network import *
from ...vpn.models import *
from ...setting.models import *


class Router:
    def __init__(self, vpn: Configuration):
        self.VpnList = {
            "openvpn": {
                "up_file": Path(__file__).resolve().parent
                / "template_router/openvpn_up.sh",
                "down_file": Path(__file__).resolve().parent
                / "template_router/openvpn_down.sh",
                "pid_file": "/tmp/openvpn.pid",
                "log_file": "/tmp/openvpn.log",
                "interface": "tun0",
                "config_file": "/tmp/openvpn.ovpn",
                "auth_file": "/tmp/openvpn.auth",
            },
            "openconnect": {
                "up_file": Path(__file__).resolve().parent
                / "template_router/openconnect_up.sh",
                "down_file": Path(__file__).resolve().parent
                / "template_router/openconnect_down.sh",
                "pid_file": "/tmp/openconnect.pid",
                "log_file": "/tmp/openconnect.log",
                "interface": "tun0",
            },
            "v2ray": {
                "up_file": Path(__file__).resolve().parent
                / "template_router/v2ray_up.sh",
                "down_file": Path(__file__).resolve().parent
                / "template_router/v2ray_down.sh",
                "pid_file": "/tmp/v2ray.pid",
                "log_file": "/tmp/v2ray.log",
                "interface": "tun0",
                "config_file": "/tmp/v2ray.json",
                "tun2socks_log_file": "/tmp/tun2socks.log",
                "dns2socks_log_file": "/tmp/dns2socks.log",
            },
            "check_vpn": Path(__file__).resolve().parent
            / "template_router/check_vpn.sh",
        }
        self.vpn = vpn
        self.general = General.objects.first()
        self.network = Network()

    def ConnectVPN(self, timeout_arg, try_count_arg):
        res = -1
        output = ""
        if isinstance(self.vpn.subclass, OpenVpnConfig):
            openvpn = self.vpn.subclass

            up_file = self.VpnList["openvpn"]["up_file"]
            pid_file = "--pid_file '{}'".format(self.VpnList["openvpn"]["pid_file"])
            log_file = "--log_file '{}'".format(self.VpnList["openvpn"]["log_file"])
            timeout = "--timeout '{}'".format(timeout_arg)
            try_count = "--try_count '{}'".format(try_count_arg)

            # write config file
            _file = self.VpnList["openvpn"]["config_file"]
            f = open(_file, "w")
            f.write(openvpn.ovpn)
            f.close()
            #
            config_file = "--config_file '{}'".format(
                self.VpnList["openvpn"]["config_file"]
            )

            username = "--username '{}'".format(openvpn.username)
            password = "--password '{}'".format(openvpn.password)
            auth_file = "--auth_file '{}'".format(self.VpnList["openvpn"]["auth_file"])
            interface = "--interface '{}'".format(self.VpnList["openvpn"]["interface"])
            log = "--log" if self.general.log else ""

            c = Execte(
                "{} {} {} {} {} {} {} {} {} {} {}".format(
                    up_file,
                    pid_file,
                    log_file,
                    timeout,
                    try_count,
                    config_file,
                    username,
                    password,
                    auth_file,
                    interface,
                    log,
                )
            )
            c.do()
            c.print()
            res = c.returncode
            output = c.getSTD()

        elif isinstance(self.vpn.subclass, OpenconnectConfig):
            openconnect = self.vpn.subclass

            up_file = self.VpnList["openconnect"]["up_file"]
            pid_file = "--pid_file '{}'".format(self.VpnList["openconnect"]["pid_file"])
            log_file = "--log_file '{}'".format(self.VpnList["openconnect"]["log_file"])
            timeout = "--timeout '{}'".format(timeout_arg)
            try_count = "--try_count '{}'".format(try_count_arg)

            protocol = "--protocol '{}'".format(openconnect.protocol)
            gateway = "--gateway '{}'".format(
                openconnect.hostname + ":" + str(openconnect.port)
            )
            username = "--username '{}'".format(openconnect.username)
            password = "--password '{}'".format(openconnect.password)
            interface = "--interface '{}'".format(
                self.VpnList["openconnect"]["interface"]
            )
            no_dtls = "--no_dtls" if openconnect.no_dtls else ""
            passtos = "--passtos" if openconnect.passtos else ""
            no_deflate = "--no_deflate" if openconnect.no_deflate else ""
            deflate = "--deflate" if openconnect.deflate else ""
            no_http_keepalive = (
                "--no_http_keepalive" if openconnect.no_http_keepalive else ""
            )
            log = "--log" if self.general.log else ""

            c = Execte(
                "{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
                    up_file,
                    pid_file,
                    log_file,
                    timeout,
                    try_count,
                    protocol,
                    gateway,
                    username,
                    password,
                    interface,
                    no_dtls,
                    passtos,
                    no_deflate,
                    deflate,
                    no_http_keepalive,
                    log,
                )
            )
            c.do()
            c.print()
            res = c.returncode
            output = c.getSTD()

        elif isinstance(self.vpn.subclass, V2rayConfig):
            v2ray = self.vpn.subclass

            up_file = self.VpnList["v2ray"]["up_file"]
            pid_file = "--pid_file '{}'".format(self.VpnList["v2ray"]["pid_file"])
            log_file = "--log_file '{}'".format(self.VpnList["v2ray"]["log_file"])
            timeout = "--timeout '{}'".format(timeout_arg)
            try_count = "--try_count '{}'".format(try_count_arg)

            # write config file
            config_file = self.VpnList["v2ray"]["config_file"]
            config_json = v2ray.config_json
            f = open(config_file, "w")
            f.write(config_json)
            f.close()
            #
            config = "--config '{}'".format(config_file)

            vpn_interface = "--vpn_interface '{}'".format(
                self.VpnList["v2ray"]["interface"]
            )
            config_json = v2ray.config_json
            js = json.loads(config_json)
            v2ray_inbounds_port = "--v2ray_inbounds_port '{}'".format(
                js["inbounds"][0]["port"]
            )
            v2ray_outbounds_address = "--v2ray_outbounds_address '{}'".format(
                v2ray.hostname
            )
            tun2socks = "--tun2socks '{}'".format(self.general.v2ray_mode)
            tun2socks_log_file = "--tun2socks_log_file '{}'".format(
                self.VpnList["v2ray"]["tun2socks_log_file"]
            )
            dns_server = (
                "--dns_server '{}'".format(self.general.dns.strip().split()[0])
                if self.general.dns_Mode == self.general.DnsMode._3
                and self.general.dns != ""
                else ""
            )
            dns_log = (
                "--dns_log '{}'".format(self.VpnList["v2ray"]["dns2socks_log_file"])
                if self.general.dns_Mode == self.general.DnsMode._3
                and self.general.dns != ""
                else ""
            )
            log = "--log" if self.general.log else ""

            c = Execte(
                "{} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
                    up_file,
                    pid_file,
                    log_file,
                    timeout,
                    try_count,
                    config,
                    vpn_interface,
                    v2ray_inbounds_port,
                    v2ray_outbounds_address,
                    tun2socks,
                    tun2socks_log_file,
                    dns_server,
                    dns_log,
                    log,
                )
            )
            c.do()
            c.print()
            res = c.returncode
            output = c.getSTD()

        else:
            res = -1
            output = "Not Implimnet Yet"

        if res == 0:
            time.sleep(5)
            if not self.check_vpn(
                self.general.CheckVpnMethod.curl, self.general.CheckVpnListMethod.three
            ):
                res = -1

        if res != 0:
            self.DisconnectVPN()

        return res, output

    def DisconnectVPN(self):
        res = -1
        output = ""
        if isinstance(self.vpn.subclass, OpenVpnConfig):
            openvpn = self.vpn.subclass

            down_file = self.VpnList["openvpn"]["down_file"]
            pid_file = "--pid_file '{}'".format(self.VpnList["openvpn"]["pid_file"])
            log_file = "--log_file '{}'".format(self.VpnList["openvpn"]["log_file"])
            config_file = "--config_file '{}'".format(
                self.VpnList["openvpn"]["config_file"]
            )
            auth_file = "--auth_file '{}'".format(self.VpnList["openvpn"]["auth_file"])
            log = "--log" if self.general.log else ""

            c = Execte(
                "{} {} {} {} {} {}".format(
                    down_file, pid_file, log_file, config_file, auth_file, log
                )
            )
            c.do()
            c.print()
            res = c.returncode
            output = c.getSTD()

        elif isinstance(self.vpn.subclass, OpenconnectConfig):
            openconnect = self.vpn.subclass

            down_file = self.VpnList["openconnect"]["down_file"]
            pid_file = "--pid_file '{}'".format(self.VpnList["openconnect"]["pid_file"])
            log_file = "--log_file '{}'".format(self.VpnList["openconnect"]["log_file"])
            log = "--log" if self.general.log else ""

            c = Execte("{} {} {} {}".format(down_file, pid_file, log_file, log))
            c.do()
            c.print()
            res = c.returncode
            output = c.getSTD()

        elif isinstance(self.vpn.subclass, V2rayConfig):
            v2ray = self.vpn.subclass

            down_file = self.VpnList["v2ray"]["down_file"]
            pid_file = "--pid_file '{}'".format(self.VpnList["v2ray"]["pid_file"])
            log_file = "--log_file '{}'".format(self.VpnList["v2ray"]["log_file"])
            vpn_interface = "--vpn_interface '{}'".format(
                self.VpnList["v2ray"]["interface"]
            )
            v2ray_outbounds_address = "--v2ray_outbounds_address '{}'".format(
                v2ray.hostname
            )
            tun2socks = "--tun2socks '{}'".format(self.general.v2ray_mode)
            tun2socks_log_file = "--tun2socks_log_file '{}'".format(
                self.VpnList["v2ray"]["tun2socks_log_file"]
            )
            dns_log = (
                "--dns_log '{}'".format(self.VpnList["v2ray"]["dns2socks_log_file"])
                if self.general.dns_Mode == self.general.DnsMode._3
                and self.general.dns != ""
                else ""
            )
            log = "--log" if self.general.log else ""

            c = Execte(
                "{} {} {} {} {} {} {} {} {}".format(
                    down_file,
                    pid_file,
                    log_file,
                    vpn_interface,
                    v2ray_outbounds_address,
                    tun2socks,
                    tun2socks_log_file,
                    dns_log,
                    log,
                )
            )
            c.do()
            c.print()
            res = c.returncode
            output = c.getSTD()

        return res, output

    def read_pid_file(self):
        pid = 0
        pid_file = ""
        if isinstance(self.vpn.subclass, OpenVpnConfig):
            openvpn = self.vpn.subclass
            pid_file = self.VpnList["openvpn"]["pid_file"]
        elif isinstance(self.vpn.subclass, OpenconnectConfig):
            openconnect = self.vpn.subclass
            pid_file = self.VpnList["openconnect"]["pid_file"]
        elif isinstance(self.vpn.subclass, V2rayConfig):
            v2ray = self.vpn.subclass
            pid_file = self.VpnList["v2ray"]["pid_file"]

        if pid_file != "" and os.path.isfile(pid_file):
            file = open(pid_file, "r")
            pid = file.read().strip()

        return pid

    def is_running(self):
        res = False

        pid = self.read_pid_file()
        if pid != 0:
            c_proc = Execte("kill -0 {}".format(pid))
            c_proc.do()
            c_proc.print()
            if c_proc.isSuccess():
                res = True

        return res

    def check_vpn(self, method=None, list_method=None):
        method = self.general.check_vpn_method if method == None else method
        list_method = (
            self.general.check_vpn_list_method if list_method == None else list_method
        )

        res = False
        if method == self.general.CheckVpnMethod.disable:
            res = True
        else:
            list = ()
            timeout = None
            retry = None

            if method == self.general.CheckVpnMethod.random:
                if (
                    isinstance(self.vpn.subclass, V2rayConfig)
                    and self.general.v2ray_mode
                    == self.general.V2rayMode.badvpn_tun2socks
                ):
                    method = self.general.CheckVpnMethod.curl
                else:
                    method = (
                        self.general.CheckVpnMethod.curl
                        if random.randint(1, 2) == 1
                        else self.general.CheckVpnMethod.ping
                    )

            if method == self.general.CheckVpnMethod.curl:
                list = self.general.check_vpn_curl_list.split()
                timeout = self.general.check_vpn_curl_timeout
                retry = self.general.check_vpn_curl_retry
            elif method == self.general.CheckVpnMethod.ping:
                list = self.general.check_vpn_ping_list.split()
                timeout = self.general.check_vpn_ping_timeout
                retry = self.general.check_vpn_ping_retry

            if len(list) == 0:
                res = False

            elif list_method == self.general.CheckVpnListMethod.strict:
                res = True
                for domain in list:
                    if domain != "":
                        if not self._check_vpn(method, domain, timeout, retry):
                            res = False
                            break

            else:
                random.shuffle(list)
                if list_method == self.general.CheckVpnListMethod.one and len(list) > 1:
                    list = list[0:1]
                elif (
                    list_method == self.general.CheckVpnListMethod.two and len(list) > 2
                ):
                    list = list[0:2]
                elif (
                    list_method == self.general.CheckVpnListMethod.three
                    and len(list) > 3
                ):
                    list = list[0:3]
                elif list_method == self.general.CheckVpnListMethod.all:
                    list = list

                res = False
                for domain in list:
                    if domain != "":
                        if self._check_vpn(method, domain, timeout, retry):
                            res = True
                            break

        return res

    def _check_vpn(self, method, domain, timeout, retry):
        check_vpn = self.VpnList["check_vpn"]
        _method = "--method '{}'".format(method)
        _domain = "--domain '{}'".format(domain)
        _timeout = "--timeout '{}'".format(timeout)
        _retry = "--retry '{}'".format(retry)
        c = Execte(
            "{} {} {} {} {}".format(check_vpn, _method, _domain, _timeout, _retry)
        )
        c.do()
        c.print()
        return c.isSuccess()
