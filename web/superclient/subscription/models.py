from django.db import models

import requests
import json
import os
import random
import string
import time
from superclient.vpn.models import OpenVpnConfig, OpenconnectConfig, V2rayConfig


class SubscriptionConfig(models.Model):

    resync = models.BooleanField(default=True)

    @property
    def subclass(self):
        if hasattr(self, "vitaminconfig"):
            return self.vitaminconfig


class VitaminConfig(SubscriptionConfig):

    main_url = models.CharField(max_length=128, default="https://v5gnet.shop")
    serverlist_json = models.CharField(
        max_length=131072,
        help_text="Please login to your account next goto json page e.g. (https://v5gnet.shop/serverslistjson) and copy content here.",
    )
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    v2ray_subscription_url = models.CharField(max_length=128)
    openvpn = models.BooleanField(default=True)
    openvpn_max_number = models.IntegerField(default=20)
    anyconnect = models.BooleanField(default=True)
    anyconnect_max_number = models.IntegerField(default=20)
    v2ray = models.BooleanField(default=True)
    v2ray_max_number = models.IntegerField(default=20)

    def update(self):

        # openvpn
        if self.openvpn:

            try:
                OpenVpnConfig.objects.filter(subscription=self).all().delete()

                servers = []

                _json = json.loads(self.serverlist_json)
                for row in _json["data"]:

                    server = row["loc"]["lp"]
                    if server != "" and server != "#" and server not in servers:
                        servers.append(self.main_url + server)

                    server = row["loc"]["lu"]
                    if server != "" and server != "#" and server not in servers:
                        servers.append(self.main_url + server)

                    server = row["loc"]["ln"]
                    if server != "" and server != "#" and server not in servers:
                        servers.append(self.main_url + server)

                random.shuffle(servers)
                if self.openvpn_max_number != 0:
                    servers = servers[0 : self.openvpn_max_number]

                for server in servers:
                    res, file = self.download(server, "/disk/media/ovpn")
                    if res:
                        openVpnConfig = OpenVpnConfig()
                        openVpnConfig.username = self.username
                        openVpnConfig.password = self.password
                        openVpnConfig.ovpn_file = file
                        openVpnConfig.subscription = self
                        openVpnConfig.save()

            except:
                pass

        else:
            OpenVpnConfig.objects.filter(subscription=self).delete()

        # anyconnect
        if self.anyconnect:

            try:
                OpenconnectConfig.objects.filter(subscription=self).all().delete()

                servers = []

                _json = json.loads(self.serverlist_json)
                for row in _json["data"]:

                    server = str(row["loc"]["cisco"]).lower()
                    if server not in servers:
                        servers.append(server)

                    for server in row["loc"]["linkciscoarr"]:
                        server = str(server).lower()
                        if server not in servers:
                            servers.append(server)

                random.shuffle(servers)
                if self.anyconnect_max_number != 0:
                    servers = servers[0 : self.anyconnect_max_number]

                for server in servers:
                    openconnectConfig = OpenconnectConfig()
                    openconnectConfig.username = self.username
                    openconnectConfig.password = self.password
                    if ":" in server:
                        openconnectConfig.hostname = server.split(":")[0]
                        openconnectConfig.port = server.split(":")[1]
                    else:
                        openconnectConfig.hostname = server
                        openconnectConfig.port = 443
                    openconnectConfig.subscription = self
                    openconnectConfig.save()

            except:
                pass

        else:
            OpenconnectConfig.objects.filter(subscription=self).delete()

        # v2ray
        if self.v2ray:

            try:
                url = self.v2ray_subscription_url
                request = requests.get(url=url)
                content = request.text
                if request.status_code == requests.status_codes.codes.ok:
                    V2rayConfig.objects.filter(subscription=self).delete()

                    servers = []

                    for server in content.split("\n"):
                        server = server.strip()
                        if server != "":
                            servers.append(server)

                    random.shuffle(servers)
                    if self.v2ray_max_number != 0:
                        servers = servers[0 : self.v2ray_max_number]

                    V2rayConfig.bulkadd(str="\n".join(servers), subscription=self)

            except:
                pass

        else:
            V2rayConfig.objects.filter(subscription=self).delete()

        return True

    @staticmethod
    def download(url: str, dest_dir: str):
        res = False

        filename = url.split("/")[-1]
        file_path = os.path.join(dest_dir, filename)

        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        while os.path.isfile(file_path):
            filename = random.choice(string.ascii_lowercase) + filename
            file_path = os.path.join(dest_dir, filename)

        request = requests.get(url, stream=True)
        if request.ok:
            with open(file_path, "wb") as f:
                for chunk in request.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
                        res = True
        return res, file_path
