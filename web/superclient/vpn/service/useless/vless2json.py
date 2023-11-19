from ..models import *

# vless://34713f55-2486-4ad3-b1e2-3eca4e6ff822@45.81.19.75:54321?type=ws&security=none&path=%2F#mokriArmin@brdg3.gvpn

vless = {
    "stats": {},
    "log": {"loglevel": "warning"},
    "policy": {
        "levels": {
            "8": {"handshake": 4, "connIdle": 300, "uplinkOnly": 1, "downlinkOnly": 1}
        },
        "system": {"statsOutboundUplink": true, "statsOutboundDownlink": true},
    },
    "inbounds": [
        {
            "tag": "socks",
            "port": 10808,
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": true, "userLevel": 8},
            "sniffing": {"enabled": true, "destOverride": ["http", "tls"]},
        },
        {
            "tag": "http",
            "port": 10809,
            "protocol": "http",
            "settings": {"userLevel": 8},
        },
    ],
    "outbounds": [
        {
            "tag": "proxy",
            "protocol": "vless",
            "settings": {
                "vnext": [
                    {
                        "address": "45.81.19.75",
                        "port": 54321,
                        "users": [
                            {
                                "encryption": "none",
                                "flow": "",
                                "id": "34713f55-2486-4ad3-b1e2-3eca4e6ff822",
                                "level": 8,
                            }
                        ],
                    }
                ]
            },
            "streamSettings": {
                "network": "ws",
                "security": "none",
                "wsSettings": {"path": "/", "headers": {"Host": ""}},
            },
            "mux": {"enabled": false},
        },
        {"tag": "direct", "protocol": "freedom", "settings": {}},
        {
            "tag": "block",
            "protocol": "blackhole",
            "settings": {"response": {"type": "http"}},
        },
    ],
    "dns": {"servers": ["8.8.8.8"]},
    "routing": {"domainStrategy": "Asls", "rules": []},
}


def generate(model: V2rayConfig):
    pass
