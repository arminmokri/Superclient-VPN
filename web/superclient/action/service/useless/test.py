#!/usr/bin/env python3

import sys
import time
import logging

from .AccessPoint import *
from .Router import Router *


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

def main():
    #access_point = AccessPoint("wlan0", "MyWifiFree", "12345678",\
    #    "192.168.4.1", "192.168.4.10", "192.168.4.20", "255.255.255.0")
    #access_point.restart()

    cfg = {
        "gateway" : "cisco2.dr-infoo.com:510",
        "username" : "greenmile",
        "password" : "atakohi",
        "priority" : "10"
    }

    router = Router()

    #router.DeleteVPN("armin")

    #time.sleep(3)

    #router.AddVPN("armin", "anyconnect", cfg)



    res, str = router.ConnectVPN("armin")
    print(res)
    print(str)
    #router.SetVPNData("armin", "vpn.data.failed", "1")

    #router.DeleteVPN("armin")

    #time.sleep(3)

    #router.AddVPN("armin", "anyconnect", cfg)
    #print(router.GetVPNData("armin", "connection.uuid"))
    

if __name__ == "__main__":
    sys.exit(main())
