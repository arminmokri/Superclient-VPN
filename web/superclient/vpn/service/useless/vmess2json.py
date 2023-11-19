from ..models import *

# vmess://eyJhZGQiOiAiNDUuODEuMTkuNzUiLCAiYWlkIjogMCwgImhvc3QiOiAiIiwgImlkIjogIjM0NzEzZjU1LTI0ODYtNGFkMy1iMWUyLTNlY2E0ZTZmZjgyMiIsICJuZXQiOiAidGNwIiwgInBhdGgiOiAiLyIsICJwb3J0IjogIjU0MzIiLCAicHMiOiAibW9rcmlBcm1pbkBicmRnMy5ndnBuIiwgInRscyI6ICJub25lIiwgInR5cGUiOiAibm9uZSIsICJ2IjogIjIifQ==

# {
#  "add": "45.81.19.75",
#  "aid": 0,
#  "host": "",
#  "id": "34713f55-2486-4ad3-b1e2-3eca4e6ff822",
#  "net": "tcp",
#  "path": "/",
#  "port": "5432",
#  "ps": "mokriArmin@brdg3.gvpn",
#  "tls": "none",
#  "type": "none",
#  "v": "2"
# }

vmess = {
    "stats": {},
    "log": {"loglevel": "warning"},
    "policy": {
        "levels": {
            "8": {"handshake": 4, "connIdle": 300, "uplinkOnly": 1, "downlinkOnly": 1}
        },
        "system": {"statsOutboundUplink": "true", "statsOutboundDownlink": "true"},
    },
    "inbounds": [
        {
            "tag": "socks",
            "port": 10808,
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": "true", "userLevel": 8},
            "sniffing": {"enabled": "true", "destOverride": ["http", "tls"]},
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
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": "45.81.19.75",
                        "port": 5432,
                        "users": [
                            {
                                "id": "34713f55-2486-4ad3-b1e2-3eca4e6ff822",
                                "alterId": 0,
                                "security": "auto",
                                "level": 8,
                            }
                        ],
                    }
                ]
            },
            "streamSettings": {"network": "tcp", "security": "none"},
            "mux": {"enabled": "false"},
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
