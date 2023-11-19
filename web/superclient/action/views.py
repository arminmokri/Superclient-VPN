from django.shortcuts import render
from pathlib import Path
from superclient.vpn.models import Configuration
from superclient.action.service.Router import Router
from .models import ServiceStatus as Status
from .service.Execte import *
from .service.Network import *


def index(request):
    status = Status.get()

    if request.method == "POST":
        if "apply" in request.POST.dict().keys():
            Network().Apply()

            if not status.apply:
                status.toggle_apply()

        elif "vpn" in request.POST.dict().keys():
            status.toggle_on()

            if status.on:
                selected_vpn = Configuration.objects.filter(
                    id=request.POST.dict()["select_vpn"]
                ).first()
                status.change_selected_vpn(selected_vpn)
            else:
                status.change_selected_vpn(None)

    submitText = "Off" if status.on else "On"
    vpn_configs = Configuration.objects.filter(enable=True).order_by("priority").all()
    vpns = [{"title": vpn.title, "id": vpn.id} for vpn in vpn_configs]
    vpns.insert(0, {"title": "auto (smart)", "id": -1})

    context = {
        "isOn": status.on,
        "vpns": vpns,
        "submitText": submitText,
        "selectedVpn": "auto (smart)"
        if status.selected_vpn is None
        else status.selected_vpn.title,
        "activeVpn_on": "Connecting..."
        if status.active_vpn is None
        else status.active_vpn.title,
        "activeVpn_off": "No Active VPN"
        if status.active_vpn is None
        else status.active_vpn.title,
    }

    return render(request, "index.html", context)


def update(request):

    #
    app_version_path = Path(__file__).resolve().parent.parent.parent.parent / "releases"
    file = open(app_version_path, "r")
    current_app_version = file.read().strip()

    #
    c = Execte("firmware --action get_release_version --repo-username-path /disk/username --repo-name-path /disk/name")
    c.do()
    available_app_version = c.stdout.strip()

    #
    can_update = False
    if available_app_version != "" and current_app_version != available_app_version:
        can_update = True

    #
    updating = 0
    if request.method == "POST":
        c = Execte(
            "firmware --action update_release --repo-username-path /disk/username --repo-name-path /disk/name --firmware-dir-path /disk/firmware --release-version-path /memory/releases --tmp-dir-path /tmp",
            False,
        )
        c.do()
        if c.returncode == 0:
            c1 = Execte("sleep 5 && reboot &", True)
            c1.do()
            updating = 1
        else:
            updating = -1

    context = {
        "current_app_version": current_app_version,
        "available_app_version": available_app_version,
        "can_update": can_update,
        "updating": updating,
    }
    return render(request, "update.html", context)


def reboot(request):

    #
    c = Execte("sleep 5 && reboot &", True)
    c.do()

    return render(request, "reboot.html")
