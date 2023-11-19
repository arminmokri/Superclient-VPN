from django.db import models
import base64
import json
from urllib.parse import urlparse, parse_qs
from django.core.validators import FileExtensionValidator
from django.dispatch import receiver
import os

from ..setting.models import General
from superclient.vpn.service import v2ray2json


class Configuration(models.Model):

    name = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=1028, blank=True)
    enable = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    success = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    last_log = models.CharField(max_length=4098, blank=True)
    subscription = models.ForeignKey(
        "subscription.SubscriptionConfig",
        on_delete=models.CASCADE,
        default=None,
        null=True,
    )

    @property
    def subclass(self):
        if hasattr(self, "openconnectconfig"):
            return self.openconnectconfig
        if hasattr(self, "l2tpconfig"):
            return self.l2tpconfig
        if hasattr(self, "openvpnconfig"):
            return self.openvpnconfig
        if hasattr(self, "shadowsocksconfig"):
            return self.shadowsocksconfig
        if hasattr(self, "v2rayconfig"):
            return self.v2rayconfig

    @property
    def type(self):
        return type(self.subclass).__name__.lower().replace("config", "")

    @property
    def title(self):
        if isinstance(self.subclass, OpenconnectConfig):
            return f"{self.name} ({self.type} / {self.subclass.protocol})"
        elif isinstance(self.subclass, V2rayConfig):
            return f"{self.name} ({self.type} / {self.subclass.protocol})"
        else:
            return f"{self.name} ({self.type})"

    @property
    def success_chance(self):
        if self.success == 0 and self.failed == 0:
            return 1  # 1
        elif self.success > 0:
            return (self.success) / (self.success + self.failed)  # 0.001 - 1
        elif self.failed > 0:
            return 1 / (self.failed * 1000)  # 0 - 0.001

    def increase_failed(self):
        self.failed = self.failed + 1
        self.save(update_fields=["failed"])

    def increase_success(self):
        self.success = self.success + 1
        self.save(update_fields=["success"])

    def add_log(self, log):
        self.last_log = log
        self.save(update_fields=["last_log"])


class L2tpConfig(Configuration):
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)


class OpenconnectConfig(Configuration):
    class Protocol(models.TextChoices):
        anyconnect = "anyconnect", "Cisco (AnyConnect)"
        nc = "nc", "Juniper Network Connect"
        gp = "gp", "Palo Alto Networks (PAN) GlobalProtect VPN"
        pulse = "pulse", "Junos Pulse VPN"
        f5 = "f5", "F5 Big-IP VPN"
        fortinet = "fortinet", "Fortinet Fortigate VPN"
        array = "array", "Array Networks SSL VPN"

    hostname = models.CharField(max_length=128)
    port = models.IntegerField()
    protocol = models.CharField(
        max_length=128, choices=Protocol.choices, default=Protocol.anyconnect
    )
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    no_dtls = models.BooleanField(default=False, help_text="Disable DTLS and ESP")
    passtos = models.BooleanField(
        default=False,
        help_text="Copy TOS / TCLASS of payload packet into DTLS and ESP packets. This is not set by default because it may leak information about the payload (for example, by differentiating voice/video traffic).",
    )
    no_deflate = models.BooleanField(
        default=False, help_text="Disable all compression."
    )
    deflate = models.BooleanField(
        default=False,
        help_text="Enable all compression, including stateful modes. By default, only stateless compression algorithms are enabled.",
    )
    no_http_keepalive = models.BooleanField(
        default=False,
        help_text="Version 8.2.2.5 of the Cisco ASA software has a bug where it will forget the client’s SSL certificate when HTTP connections are being re-used for multiple requests. So far, this has only been seen on the initial connection, where the server gives an HTTP/1.0 redirect response with an explicit Connection: Keep-Alive directive. OpenConnect as of v2.22 has an unconditional workaround for this, which is never to obey that directive after an HTTP/1.0 response.",
    )

    def save(self, *args, **kwargs):

        if self.name == None or self.name == "":
            self.name = self.hostname

        super(OpenconnectConfig, self).save(*args, **kwargs)


class ShadowSocksConfig(Configuration):

    hostname = models.CharField(max_length=128)
    port = models.IntegerField()
    password = models.CharField(max_length=128)

    class Encryption(models.TextChoices):
        chacha20_ietf_poly = "chacha20poly", "chacha20-ietf-poly1305"
        aes_256_gcm = "256gcm", "aes-256-gcm"
        aes_256_ctr = "256ctr", "aes-256-ctr"
        aes_256_cfb = "256cfb", "aes-256-cfb"

    encryption = models.CharField(max_length=12, choices=Encryption.choices)


class OpenVpnConfig(Configuration):
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    ovpn_file = models.FileField(
        upload_to="ovpn/", default=None, validators=[FileExtensionValidator(["ovpn"])]
    )

    @property
    def ovpn(self):
        try:
            _file = open(self.ovpn_file.path, "r")
            content = _file.read()
            _file.close()
            return content
        except Exception as e:
            return None

    def save(self, *args, **kwargs):

        if self.name == None or self.name == "":
            self.name = str(os.path.basename(self.ovpn_file.name))

        super(OpenVpnConfig, self).save(*args, **kwargs)


@receiver(models.signals.post_delete, sender=OpenVpnConfig)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.ovpn_file:
        if os.path.isfile(instance.ovpn_file.path):
            os.remove(instance.ovpn_file.path)


@receiver(models.signals.pre_save, sender=OpenVpnConfig)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = OpenVpnConfig.objects.get(pk=instance.pk).ovpn_file
    except OpenVpnConfig.DoesNotExist:
        return False

    new_file = instance.ovpn_file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class V2rayConfig(Configuration):
    class Protocol(models.TextChoices):
        vmess = "vmess", "VMESS"
        vless = "vless", "VLESS"
        trojan = "trojan", "TROJAN"

    class Network(models.TextChoices):
        vmess = "tcp", "TCP"
        vless = "ws", "WebSocket"

    class Tls(models.TextChoices):
        tls = "tls", "TLS"
        none = "none", "None"

    protocol = models.CharField(max_length=8, choices=Protocol.choices)
    hostname = models.CharField(max_length=128)
    # port = models.IntegerField(null=True)
    # v = models.CharField(max_length=8, default='2')
    # uid = models.CharField(max_length=64, blank=True)
    # alter_id = models.CharField(max_length=64, null=True, blank=True)
    # tls = models.CharField(max_length=8, choices=Tls.choices, blank=True)
    # tls_allow_insecure = models.BooleanField(default=False)
    # network = models.CharField(max_length=8, choices=Network.choices, blank=True)
    # ws_path = models.CharField(max_length=512, null=True, blank=True)
    # ws_host = models.CharField(max_length=256, null=True, blank=True)
    # ws_sni = models.CharField(max_length=512, null=True, blank=True)
    config_url = models.CharField(max_length=8192)

    # vmess
    # address
    # port
    # uuid
    # alter_id
    # security chacha20-poly1305 aes-128-gcm auto none zero
    # network tcp kcp ws h2 quic grpc
    # head_type none http
    # request_host (host/ws host/h2 host)/QUIC security
    # path (ws path/h2 path)/QUIC key/kcp seed/gRPC serviceName
    # tls "" tls xtls
    # sni
    # uTLS "" chrome firefox safari randomized
    # alpn "" h2 http/1.1 h2,http/1.1
    # allowInsecure "" true false

    # vless
    # address
    # port
    # uuid
    # flow
    # encryption
    # network tcp kcp ws h2 quic grpc
    # head_type none http
    # request_host (host/ws host/h2 host)/QUIC security
    # path (ws path/h2 path)/QUIC key/kcp seed/gRPC serviceName
    # tls "" tls xtls
    # sni
    # uTLS "" chrome firefox safari randomized
    # alpn "" h2 http/1.1 h2,http/1.1
    # allowInsecure "" true false

    # trojan
    # address
    # port
    # password
    # flow
    # network tcp kcp ws h2 quic grpc
    # head_type none http
    # request_host (host/ws host/h2 host)/QUIC security
    # path (ws path/h2 path)/QUIC key/kcp seed/gRPC serviceName
    # tls "" tls xtls
    # sni
    # uTLS "" chrome firefox safari randomized
    # alpn "" h2 http/1.1 h2,http/1.1
    # allowInsecure "" true false

    # config_type = 'property'

    @property
    def config_json(self):
        general = General.objects.first()
        dns = ",".join(general.dns.strip().split())
        if self.protocol == self.Protocol.vmess:
            return v2ray2json.generateConfig(self.config_url, dns_list=dns)
        elif self.protocol == self.Protocol.vless:
            return v2ray2json.generateConfig(self.config_url, dns_list=dns)
        elif self.protocol == self.Protocol.trojan:
            return v2ray2json.generateConfig(self.config_url, dns_list=dns)
        else:
            return None

    def save(self, *args, **kwargs):

        protocol, name, hostname = self.decode(self.config_url)
        if self.name == None or self.name == "":
            self.name = name
        self.protocol = protocol
        self.hostname = hostname

        super(V2rayConfig, self).save(*args, **kwargs)

    @staticmethod
    def decode(config_url):
        temp = config_url.split("://")
        protocol = temp[0]
        raw_config = temp[1]
        if protocol == V2rayConfig.Protocol.vmess:

            _len = len(raw_config)
            if _len % 4 > 0:
                raw_config += "=" * (4 - _len % 4)

            b64decode = base64.b64decode(raw_config).decode(
                encoding="utf-8", errors="ignore"
            )
            _json = json.loads(b64decode, strict=False)

            name = _json.get("ps")
            hostname = _json.get("add")

        elif protocol == V2rayConfig.Protocol.vless:
            parsed_url = urlparse(config_url)
            _netloc = parsed_url.netloc.split("@")

            name = parsed_url.fragment
            hostname = _netloc[1].split(":")[0]
            port = _netloc[1].split(":")[1]
            uid = _netloc[0]

            netquery = dict(
                (k, v if len(v) > 1 else v[0])
                for k, v in parse_qs(parsed_url.query).items()
            )

        elif protocol == V2rayConfig.Protocol.trojan:
            parsed_url = urlparse(config_url)
            _netloc = parsed_url.netloc.split("@")

            name = parsed_url.fragment
            hostname = _netloc[1].split(":")[0]
            port = _netloc[1].split(":")[1]
            uid = _netloc[0]

            netquery = dict(
                (k, v if len(v) > 1 else v[0])
                for k, v in parse_qs(parsed_url.query).items()
            )

        return protocol, name, hostname

    @staticmethod
    def bulkadd(str: str, subscription=None):
        str = str.strip()
        for line in str.split("\n"):
            if line != "":
                line = line.strip()
                try:
                    v2rayConfig = V2rayConfig()
                    v2rayConfig.subscription = subscription
                    v2rayConfig.config_url = line
                    v2rayConfig.save()
                except:
                    pass
