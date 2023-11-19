import nmcli

# local
from .Execte import *


class Router1:
    def __init__(self):
        self.VpnProtocolList = {
            "anyconnect": {
                "run_script": "./template/up_aynconnect.sh",
            },
        }
        self.VPNList = []

    def AddVPN(self, id, protocol, cfg):

        if protocol == "anyconnect":
            gateway = cfg["gateway"]
            username = cfg["username"]
            password = cfg["password"]
            priority = cfg["priority"]
            full_cfg = {
                "vpn.service-type": "openconnect",
                "vpn.data": """
authtype=password, 
autoconnect-flags=2, 
certsigs-flags=2, 
cookie-flags=2, 
enable_csd_trojan=no, 
gateway={}, 
gateway-flags=2, 
gwcert-flags=2, 
lasthost-flags=2, 
pem_passphrase_fsid=yes, 
prevent_invalid_cert=no, 
protocol=anyconnect, 
resolve-flags=2, 
stoken_source=disabled, 
xmlconfig-flags=2, 
service-type=openconnect,
username={}, 
password={}, 
priority={}, 
success=0, 
failed=0
""".format(
                    gateway, username, password, priority
                ),
                "vpn.secrets": """
""".format(),
                "ipv4.method": "auto",
                "ipv6.method": "auto",
            }
            nmcli.connection.add("vpn", full_cfg, "*", id, False)
        else:
            pass

    def DeleteVPN(self, id):
        nmcli.connection.delete(id)

    def GetVPNData(self, id, cfg):
        if "vpn.data." in cfg:
            list = nmcli.connection.show(id)["vpn.data"].split(",")
            vpndataitem = cfg[9:]
            for x in list:
                key = x.split("=")[0].strip()
                value = x.split("=")[1].strip()
                if key == vpndataitem:
                    return value
        else:
            return nmcli.connection.show(id)[cfg]

    def SetVPNData(self, id, cfg, data):
        if "vpn.data." in cfg:
            list = nmcli.connection.show(id)["vpn.data"].split(",")
            vpndataitem = cfg[9:]
            for x in list:
                key = x.split("=")[0].strip()
                if key == vpndataitem:
                    list.remove(x)
                    list.append("{}={}".format(vpndataitem, data))
                    break
            nmcli.connection.modify(id, {"vpn.data": ", ".join(list)})
        else:
            nmcli.connection.modify(id, {cfg: data})

    def _updateFailedSuccess(self, id, res):
        if res != 0:
            failed = int(self.GetVPNData(id, "vpn.data.failed")) + 1
            self.SetVPNData(id, "vpn.data.failed", failed)
        else:
            success = int(self.GetVPNData(id, "vpn.data.success")) + 1
            self.SetVPNData(id, "vpn.data.failed", success)

    def ConnectVPN(self, id):
        protocol = self.GetVPNData(id, "vpn.data.protocol")
        res = -1
        output = ""
        if protocol == "anyconnect":
            run_script = self.VpnProtocolList["anyconnect"]["run_script"]
            username = self.GetVPNData(id, "vpn.data.username")
            password = self.GetVPNData(id, "vpn.data.password")
            c1 = Execte("{} {} {} {}".format(run_script, id, username, password))
            c1.do()

            list = c1.stdout.split("\n")
            if len(list) > 20:
                list = list[-20:]
            output = "\n".join(list)

            if "Error: Connection activation failed:" in output:
                res = -1
            else:
                res = 0

        else:
            res = -1
            output = "Not Implimnet Yet"

        self._updateFailedSuccess(id, res)
        return res, output

    def LoadVPN(self):
        list = nmcli.connection()
        for x in list:
            if (
                x.conn_type == "vpn" or x.conn_type == "tun"
            ) and x.name not in self.VPNList:
                self.VPNList.append(x.name)
