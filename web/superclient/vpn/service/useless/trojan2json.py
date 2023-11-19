import json
from pathlib import Path


def generate(model, general):

    # read template
    f = open(Path(__file__).resolve().parent / "trojan_tempalate.json", "r")
    template = f.read()

    # load json
    _json = json.loads(template)

    # get childs
    _log = _json["log"]
    _dns = _json["dns"]
    _dns_servers = _dns["servers"]
    _outbounds = _json["outbounds"][0]
    _outbounds_servers = _outbounds["settings"]["servers"][0]
    _outbounds_tlsSettings = _outbounds["streamSettings"]["tlsSettings"]

    # set values
    if general.log:
        _log["loglevel"] = "Info"
    else:
        _log["loglevel"] = "None"

    # if general.dns != "":
    #  for dns in general.dns.split():
    #    _dns_servers.append(dns)

    _outbounds_servers["password"] = model.uid
    _outbounds_servers["address"] = model.host
    _outbounds_servers["port"] = model.port
    _outbounds_tlsSettings["serverName"] = model.ws_sni

    return json.dumps(_json)
