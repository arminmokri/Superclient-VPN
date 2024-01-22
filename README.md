# Superclient-VPN
### Please support my repo with your star.
**Superclient-VPN** is a router with multi vpn client protocols to keep your VPN always *on*, for all Linux embedded boards and written in Django.

## Features
- Hardware
  - Support all Linux embedded boards such as Raspberry Pi, Orange Pi, etc
  - Support all wire and wireless on-board interfaces
  - Support all wire and wireless USB interfaces

- Network
  - Support DHCP server (dnsmasq, isc-dhcp-server) on wire and wireless interfaces
  - Support Hostpot on wireless interfaces
  - Support DHCP client or static on wire interfaces
  - Support DHCP client or static on wireless interfaces

- VPN
  - Auto-connect to the best VPN between all connections
  - Auto reconnect to the next VPN between all connections on any failure
  - Support Openvpn
  - Support OpenConnect (Cisco AnyConnect, Juniper Network Connect, and etc)
  - Support V2ray (vmess, trojan, vless, and etc)
  - Add multiple configurations per each VPN protocol
  - logging about VPN connection quality to learn the best VPN connections

- Web
  - Simple web UI

## Install and Run the Project
1. Connect your embedded board to the internet
2. Connect to the shell of your embedded board via SSH or etc
3. run `cd ~`
4. run `sudo apt install git`
5. run `git clone https://github.com/arminmokri/Superclient-VPN.git`
6. run `cd Superclient-VPN/bin`
7. run `sudo ./init.sh`
8. Wait until the process ends and your embedded board going to reboot
9. Connect to the shell of your embedded board again
10. run `cd ~ `
11. run `rm -rf Superclient-VPN`
12. run `sudo firmware --action "init_release" --repo-username "arminmokri" --repo-username-path "/disk/username" --repo-name "Superclient-VPN" --repo-name-path "/disk/name" --firmware-dir-path "/disk/firmware" --tmp-dir-path "/tmp"`
13. `sudo reboot`
14. Find your embedded board IP and go to web UI http://IP
