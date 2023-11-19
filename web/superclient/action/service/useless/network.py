import os


def get_interfaces():
    return get_eth_interfaces() + get_wlan_interfaces()


def get_eth_interfaces():
    addrs = []
    for path in os.listdir("/sys/class/net"):
        if os.path.isdir("/sys/class/net/" + path + "/phydev"):
            addrs.append(path)
    addrs.sort()
    return addrs


def get_wlan_interfaces():
    addrs = []
    for path in os.listdir("/sys/class/net"):
        if os.path.isdir("/sys/class/net/" + path + "/wireless"):
            addrs.append(path)
    addrs.sort()
    return addrs


def get_first_eth_interface():
    return get_eth_interfaces()[0]


def get_first_wlan_interface():
    return get_wlan_interfaces()[0]
