#!/usr/bin/env python3
"""network-playbook CLI. Standard library only; external tools are optional.

  np.py path                       print the data directory and how it was chosen
  np.py init <slug> --name "..."   create a site workspace
  np.py scan [--site S] [--iface I] [--cidr C]   ARP + mDNS sweep, saved to scans/
  np.py diff [--site S] [--scan F] compare a scan with the definition
  np.py validate [--site S | --file F]           integrity and readiness report
  np.py build [--site S] [--date YYYY-MM-DD]     render the PDF and machine JSON

Output is JSON on stdout. Exit code 1 means errors were found.
"""
import argparse, collections, datetime as dt, hashlib, ipaddress, json, os, re
import shutil, socket, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

NAME = "network-playbook"
ROOT = Path(__file__).resolve().parent.parent
SECRET_KEY = re.compile(r"(password|passwd|passphrase|psk|secret|token|api_?key|private_?key)", re.I)
WIRELESS = {"wifi", "virtual"}
ICONS = {"modem": "bridge", "ont": "bridge", "router": "firewall", "firewall": "firewall",
         "switch": "switch", "ap": "w-ap", "server": "server", "nas": "server"}


def data_dir():
    home = Path.home()
    xdg = Path(os.environ.get("XDG_DATA_HOME", home / ".local/share")) / "claude-plugins"
    if os.environ.get("NETWORK_PLAYBOOK_HOME"):
        return Path(os.environ["NETWORK_PLAYBOOK_HOME"]), "NETWORK_PLAYBOOK_HOME"
    if os.environ.get("CLAUDE_USER_DATA"):
        return Path(os.environ["CLAUDE_USER_DATA"]) / NAME, "CLAUDE_USER_DATA"
    if (home / ".claude-user-data").is_dir():
        return home / ".claude-user-data" / NAME, "existing ~/.claude-user-data"
    if xdg.is_dir():
        return xdg / NAME, "existing XDG claude-plugins root"
    return home / ".claude-user-data" / NAME, "default"


def config():
    p = data_dir()[0] / "config.json"
    return json.loads(p.read_text()) if p.exists() else {}


def site_dir(slug):
    slug = slug or config().get("default_site")
    if not slug:
        sites = data_dir()[0] / "sites"
        found = [p.name for p in sites.iterdir()] if sites.is_dir() else []
        if len(found) != 1:
            sys.exit(f"No default site. Pass --site. Found: {found}")
        slug = found[0]
    path = data_dir()[0] / "sites" / slug
    if not path.is_dir():
        sys.exit(f"No such site: {path}")
    return path


def out(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


# ---------- init ----------
def cmd_init(a):
    base = data_dir()[0]
    site = base / "sites" / a.slug
    if (site / "network.json").exists():
        sys.exit(f"Already exists: {site}/network.json")
    for sub in ("photos", "scans", "releases"):
        (site / sub).mkdir(parents=True, exist_ok=True)
    (site / ".gitignore").write_text(".build/\n")
    skeleton = {
        "schema_version": 1,
        "site": {"name": a.name or a.slug, "slug": a.slug, "address": "", "summary": ""},
        "racks": [], "devices": [], "cables": [], "prefixes": [], "wireless": [],
        "internet": {"provider": {}, "circuits": [], "public_ip": {}},
        "pace": {}, "services": [],
        "remote_access": {"tailscale": {"nodes": []}, "cloudflare_tunnels": [], "port_forwards": [], "ddns": []},
        "dns": {"resolver": {}, "overrides": [], "zones": []},
        "photos": [], "plot": [],
        "rebuild": {"jump_kit": [], "move_out": [], "phases": [], "reconstitution": []},
        "open_questions": [], "changelog": [],
    }
    (site / "network.json").write_text(json.dumps(skeleton, indent=2) + "\n")
    cfg_path = base / "config.json"
    cfg = config()
    cfg.setdefault("default_site", a.slug)
    cfg.setdefault("publish", {"drive_folder": ""})
    cfg.setdefault("footer_line", "")
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
    out({"site": str(site), "config": str(cfg_path)})


# ---------- scan ----------
def default_route():
    _, o = run(["ip", "-j", "route", "show", "default"])
    routes = json.loads(o or "[]")
    return routes[0]["dev"] if routes else None


def iface_cidr(iface):
    _, o = run(["ip", "-j", "-4", "addr", "show", iface])
    for link in json.loads(o or "[]"):
        for ai in link.get("addr_info", []):
            return str(ipaddress.ip_interface(f"{ai['local']}/{ai['prefixlen']}").network), ai["local"]
    return None, None


def arp_sweep(iface, cidr):
    target = [cidr] if cidr else ["--localnet"]
    if shutil.which("arp-scan"):
        for prefix in (["sudo", "-n"], []):
            code, o = run(prefix + ["arp-scan", f"--interface={iface}", *target], 120)
            rows = re.findall(r"^(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f:]{17})\s*(.*)$", o, re.M | re.I)
            if rows:
                return "arp-scan", [{"ip": i, "mac": m.lower(), "vendor": v.strip()} for i, m, v in rows]
    if shutil.which("nmap") and cidr:
        run(["nmap", "-sn", "-n", cidr], 120)  # populates the neighbour table
    _, o = run(["ip", "-j", "neigh", "show", "dev", iface])
    rows = [{"ip": n["dst"], "mac": n["lladdr"].lower(), "vendor": ""} for n in json.loads(o or "[]")
            if "lladdr" in n and ":" not in n["dst"]]
    return "ip-neigh", rows


def mdns():
    if not shutil.which("avahi-browse"):
        return {}
    _, o = run(["avahi-browse", "-aprt", "--resolve"], 20)
    found = collections.defaultdict(lambda: {"hostname": "", "services": set()})
    for line in o.splitlines():
        f = line.split(";")
        if len(f) >= 9 and f[0] == "=" and f[2] == "IPv4":
            found[f[7]]["hostname"] = f[6]
            found[f[7]]["services"].add(f[4])
    return {k: {"hostname": v["hostname"], "services": sorted(v["services"])} for k, v in found.items()}


def rdns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except OSError:
        return ""


def cmd_scan(a):
    site = site_dir(a.site)
    iface = a.iface or default_route()
    if not iface:
        sys.exit("No default route; pass --iface.")
    cidr, own_ip = iface_cidr(iface)
    cidr = a.cidr or cidr
    method, hosts = arp_sweep(iface, cidr)
    seen = {}
    for h in hosts:
        seen.setdefault(h["ip"], h)
    hosts = sorted(seen.values(), key=lambda h: ipaddress.ip_address(h["ip"]))
    per_mac = collections.Counter(h["mac"] for h in hosts)
    services = mdns()
    socket.setdefaulttimeout(2)
    with ThreadPoolExecutor(16) as pool:
        names = list(pool.map(rdns, [h["ip"] for h in hosts]))
    for h, name in zip(hosts, names):
        h["rdns"] = name
        h["mdns"] = services.get(h["ip"], {})
        h["locally_administered_mac"] = h["mac"][1] in "26ae"
        h["proxy_arp_suspect"] = per_mac[h["mac"]] >= 10
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    result = {"taken": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "method": method,
              "interface": iface, "cidr": cidr, "scanner_ip": own_ip, "hosts": hosts}
    path = site / "scans" / f"scan-{stamp}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    out({"file": str(path), "method": method, "interface": iface, "cidr": cidr, "hosts": len(hosts),
         "proxy_arp_suspects": sorted({h["mac"] for h in hosts if h["proxy_arp_suspect"]})})


# ---------- model helpers ----------
def load(path):
    return json.loads(Path(path).read_text())


def ips_of(dev):
    for i in dev.get("interfaces", []):
        for a in i.get("ip_addresses", []):
            yield i, a


def macs_of(dev):
    return {i["mac"].lower() for i in dev.get("interfaces", []) if i.get("mac")}


def is_physical(iface):
    return iface.get("type", "rj45") not in WIRELESS


# ---------- diff ----------
def cmd_diff(a):
    site = site_dir(a.site)
    scans = sorted((site / "scans").glob("scan-*.json"))
    if not a.scan and not scans:
        sys.exit("No scans yet.")
    scan = load(a.scan or scans[-1])
    net = load(site / "network.json")
    by_mac, by_ip = {}, {}
    for d in net["devices"]:
        for m in macs_of(d):
            by_mac[m] = d
        for _, ip in ips_of(d):
            by_ip[ip["address"]] = d
    cidr = ipaddress.ip_network(scan["cidr"]) if scan.get("cidr") else None
    new, moved, known, seen = [], [], [], set()
    for h in scan["hosts"]:
        d = by_mac.get(h["mac"])
        if d:
            seen.add(d["id"])
            recorded = [ip["address"] for _, ip in ips_of(d)]
            if h["ip"] in recorded:
                known.append({"device": d["id"], "ip": h["ip"]})
            else:
                moved.append({"device": d["id"], "scan_ip": h["ip"], "recorded": recorded})
        elif h["ip"] in by_ip:
            d = by_ip[h["ip"]]
            seen.add(d["id"])
            moved.append({"device": d["id"], "ip": h["ip"], "scan_mac": h["mac"],
                          "recorded_macs": sorted(macs_of(d)), "note": "same IP, unrecorded MAC"})
        else:
            new.append(h)
    missing = []
    for d in net["devices"]:
        addrs = [ip["address"] for _, ip in ips_of(d)]
        in_scope = any(cidr and ipaddress.ip_address(x) in cidr for x in addrs)
        if in_scope and d["id"] not in seen:
            missing.append({"device": d["id"], "recorded": addrs})
    out({"scan": scan.get("taken"), "cidr": scan.get("cidr"), "known": len(known),
         "new": new, "changed": moved, "missing": missing})


# ---------- validate ----------
def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield f"{path}.{k}", k, v
            yield from walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for n, v in enumerate(node):
            yield from walk(v, f"{path}[{n}]")


def validate(net, site=None):
    err, warn = [], []
    for path, key, value in walk(net):
        if SECRET_KEY.search(key) and not key.endswith("_ref") and value:
            err.append(f"{path}: looks like a secret value; store a *_ref pointer instead")

    devices, seen_macs, seen_ips = {}, {}, {}
    for d in net.get("devices", []):
        if d["id"] in devices:
            err.append(f"duplicate device id {d['id']}")
        devices[d["id"]] = d
    prefixes = {}
    for p in net.get("prefixes", []):
        try:
            prefixes[p["id"]] = ipaddress.ip_network(p["cidr"])
        except ValueError as e:
            err.append(f"prefix {p.get('id')}: {e}")
            continue
        net_ = prefixes[p["id"]]
        for key in ("gateway",):
            if p.get(key) and ipaddress.ip_address(p[key]) not in net_:
                err.append(f"prefix {p['id']}: {key} outside {net_}")
        for r in p.get("ip_ranges", []):
            for key in ("start", "end"):
                if ipaddress.ip_address(r[key]) not in net_:
                    err.append(f"prefix {p['id']}: range {key} {r[key]} outside {net_}")
    ranges = [(ipaddress.ip_address(r["start"]), ipaddress.ip_address(r["end"]))
              for p in net.get("prefixes", []) for r in p.get("ip_ranges", []) if r.get("kind", "dhcp") == "dhcp"]

    for d in devices.values():
        seen_if = set()
        for i in d.get("interfaces", []):
            if i["id"] in seen_if:
                err.append(f"{d['id']}: duplicate interface {i['id']}")
            seen_if.add(i["id"])
            mac = (i.get("mac") or "").lower()
            if mac:
                if not re.fullmatch(r"([0-9a-f]{2}:){5}[0-9a-f]{2}", mac):
                    err.append(f"{d['id']}:{i['id']}: bad MAC {mac}")
                if mac in seen_macs and seen_macs[mac] != d["id"]:
                    err.append(f"MAC {mac} on both {seen_macs[mac]} and {d['id']}")
                seen_macs[mac] = d["id"]
            for a in i.get("ip_addresses", []):
                ip = ipaddress.ip_address(a["address"])
                if a["address"] in seen_ips:
                    err.append(f"IP {ip} on both {seen_ips[a['address']]} and {d['id']}")
                seen_ips[a["address"]] = d["id"]
                pid = a.get("prefix")
                if pid and pid not in prefixes:
                    err.append(f"{d['id']}: unknown prefix {pid}")
                elif pid and ip not in prefixes[pid]:
                    err.append(f"{d['id']}: {ip} outside prefix {pid}")
                if a.get("assignment") == "reservation" and not mac:
                    warn.append(f"{d['id']}:{i['id']}: reservation {ip} has no MAC recorded")
                if a.get("assignment") in ("static", "reservation") and any(s <= ip <= e for s, e in ranges):
                    warn.append(f"{d['id']}: fixed address {ip} is inside a DHCP range")
        if d.get("hosted_on") and d["hosted_on"] not in devices:
            err.append(f"{d['id']}: hosted_on {d['hosted_on']} unknown")

    used = {}
    for c in net.get("cables", []):
        for end in ("a", "b"):
            e = c[end]
            dev = devices.get(e["device"])
            if not dev:
                err.append(f"cable {c['id']}: unknown device {e['device']}")
            elif e["interface"] not in {i["id"] for i in dev.get("interfaces", [])}:
                err.append(f"cable {c['id']}: {e['device']} has no interface {e['interface']}")
            key = f"{e['device']}:{e['interface']}"
            if key in used:
                err.append(f"{key} used by cables {used[key]} and {c['id']}")
            used[key] = c["id"]
    ids = [c["id"] for c in net.get("cables", [])]
    for cid, n in collections.Counter(ids).items():
        if n > 1:
            err.append(f"duplicate cable id {cid}")

    ra = net.get("remote_access", {})
    for n in ra.get("tailscale", {}).get("nodes", []):
        if n.get("device") and n["device"] not in devices:
            err.append(f"tailscale node {n.get('name')}: unknown device {n['device']}")
    for t in ra.get("cloudflare_tunnels", []):
        if t.get("connector") and t["connector"] not in devices:
            err.append(f"tunnel {t.get('name')}: unknown connector {t['connector']}")
    for s in net.get("services", []):
        if s.get("host") and s["host"] not in devices:
            err.append(f"service {s.get('name')}: unknown host {s['host']}")
    for j in net.get("rebuild", {}).get("jump_kit", []):
        if j not in devices:
            err.append(f"jump_kit: unknown device {j}")

    photo_ids = set()
    for p in net.get("photos", []):
        photo_ids.add(p["id"])
        if site and not (site / p["file"]).exists():
            err.append(f"photo {p['id']}: missing file {p['file']}")
    for d in devices.values():
        for p in d.get("photos", []):
            if p not in photo_ids:
                err.append(f"{d['id']}: unknown photo {p}")

    step_ids, steps = set(), []
    for ph in net.get("rebuild", {}).get("phases", []):
        if not ph.get("pause_point"):
            warn.append(f"phase {ph.get('id')}: no pause_point")
        if len(ph.get("steps", [])) > 9:
            warn.append(f"phase {ph.get('id')}: {len(ph['steps'])} steps; split it (aim for 5 to 9)")
        for s in ph.get("steps", []):
            for dep in s.get("depends_on", []):
                if dep not in step_ids:
                    err.append(f"step {s['id']}: depends on {dep}, which is not earlier in the plan")
            step_ids.add(s["id"])
            steps.append(s)
            if not s.get("verify"):
                warn.append(f"step {s['id']}: no verify check")

    gaps = []
    phys = [d for d in devices.values() if not d.get("hosted_on") and d.get("role") != "client"]
    if not net.get("internet", {}).get("circuits"):
        gaps.append("no internet circuit recorded")
    if not net.get("prefixes"):
        gaps.append("no prefixes recorded")
    if not ranges:
        gaps.append("no DHCP range recorded")
    if not any(a.get("assignment") == "reservation" for d in devices.values() for _, a in ips_of(d)):
        gaps.append("no IP reservations recorded")
    if not net.get("cables"):
        gaps.append("no cables recorded")
    for d in phys:
        if d.get("role") in ("router", "firewall", "switch", "modem", "ont"):
            ports = [i for i in d.get("interfaces", []) if is_physical(i)]
            if not ports:
                gaps.append(f"{d['id']}: no port map")
            elif not all(i.get("position") for i in ports):
                gaps.append(f"{d['id']}: ports without a faceplate position")
    for name in ("internet", "admin_access"):
        if not net.get("pace", {}).get(name, {}).get("primary"):
            gaps.append(f"no PACE plan for {name}")
    if not steps:
        gaps.append("no rebuild steps")
    if not net.get("rebuild", {}).get("reconstitution"):
        gaps.append("no reconstitution checks")
    return err, warn, gaps


def resolve_input(a):
    if getattr(a, "file", None):
        return load(a.file), Path(a.file).parent
    site = site_dir(a.site)
    return load(site / "network.json"), site


def cmd_validate(a):
    net, site = resolve_input(a)
    err, warn, gaps = validate(net, site)
    out({"errors": err, "warnings": warn, "readiness_gaps": gaps, "open_questions": net.get("open_questions", []),
         "playbook_ready": not err and not gaps})
    sys.exit(1 if err else 0)


# ---------- build ----------
def topology(net):
    devices = {d["id"]: d for d in net["devices"]}
    adj = collections.defaultdict(list)
    for c in net.get("cables", []):
        a, b = c["a"]["device"], c["b"]["device"]
        adj[a].append((b, c["id"]))
        adj[b].append((a, c["id"]))
    roots = [c["device"] for c in net.get("internet", {}).get("circuits", []) if c.get("device") in devices]
    if not roots:
        roots = [d["id"] for d in net["devices"] if d.get("role") in ("modem", "ont", "router", "firewall")][:1]
    # A circuit lands on the router, but any modem or ONT cabled to it sits upstream.
    roots = [next((n for n, _ in adj[r] if devices[n].get("role") in ("modem", "ont")), r) for r in roots]
    level, queue = {r: 1 for r in roots}, list(roots)
    while queue:
        cur = queue.pop(0)
        for nxt, _ in adj[cur]:
            if nxt not in level:
                level[nxt] = level[cur] + 1
                queue.append(nxt)
    rows = collections.defaultdict(list)
    for dev_id, lv in level.items():
        rows[lv].append(dev_id)
    widest = max([len(v) for v in rows.values()] + [1])
    gap, tier = 5.5, 5
    nodes, pos = [{"id": "internet", "name": "Internet", "ip": "", "icon": "cloud", "x": 0, "y": 0}], {}
    for lv, ids in sorted(rows.items()):
        for n, dev_id in enumerate(ids):
            d = devices[dev_id]
            x = (n - (len(ids) - 1) / 2) * gap
            pos[dev_id] = (x, lv)
            addr = next((ip["address"] for _, ip in ips_of(d)), "")
            nodes.append({"id": dev_id, "name": d.get("name", dev_id), "ip": addr,
                          "icon": ICONS.get(d.get("role"), "monitor"), "x": x, "y": lv * tier})
    edges = [{"x1": 0, "y1": 0, "x2": pos[r][0], "y2": tier, "label": ""} for r in roots]
    for c in net.get("cables", []):
        a, b = c["a"]["device"], c["b"]["device"]
        if a in pos and b in pos:
            edges.append({"x1": pos[a][0], "y1": pos[a][1] * tier, "x2": pos[b][0], "y2": pos[b][1] * tier, "label": c["id"]})
    unit = round(min(0.6, 16.5 / max(widest * gap, 1)), 2)
    return {"nodes": nodes, "edges": edges, "unit_cm": unit, "unconnected": [d for d in devices if d not in pos and not devices[d].get("hosted_on")]}


def derive(net):
    devices = {d["id"]: d for d in net["devices"]}
    far = {}
    for c in net.get("cables", []):
        a, b = c["a"], c["b"]
        far[(a["device"], a["interface"])] = (b, c["id"])
        far[(b["device"], b["interface"])] = (a, c["id"])

    def named(e):
        d = devices[e["device"]]
        label = next((i.get("label") for i in d["interfaces"] if i["id"] == e["interface"]), None)
        return f"{d.get('name', d['id'])} {label or e['interface']}"

    plates = []
    for d in net["devices"]:
        ports = [i for i in d.get("interfaces", []) if is_physical(i) and i.get("position")]
        if not ports:
            continue
        groups = collections.defaultdict(list)
        for i in ports:
            groups[(i.get("face", "rear"), i.get("row", 1))].append(i)
        faces = []
        for (face, row), items in sorted(groups.items()):
            items.sort(key=lambda i: i["position"])
            cells = []
            for i in items:
                f = far.get((d["id"], i["id"]))
                cells.append({"position": i["position"], "label": i.get("label", i["id"]), "use": i.get("use", "lan"),
                              "os_name": i.get("os_name", ""), "far": named(f[0]) if f else "", "cable": f[1] if f else ""})
            for start in range(0, len(cells), 12):
                faces.append({"face": face, "row": row, "ports": cells[start:start + 12]})
        plates.append({"device": d["id"], "name": d.get("name", d["id"]), "model": " ".join(filter(None, [d.get("make"), d.get("model")])),
                       "faces": faces, "photos": d.get("photos", []), "notes": d.get("notes", "")})

    addresses = []
    for d in net["devices"]:
        for i, a in ips_of(d):
            addresses.append({"ip": a["address"], "device": d.get("name", d["id"]), "mac": i.get("mac", ""),
                              "assignment": a.get("assignment", ""), "prefix": a.get("prefix", ""), "dns_name": a.get("dns_name", "")})
    addresses.sort(key=lambda r: ipaddress.ip_address(r["ip"]))

    cables = [{"id": c["id"], "from": named(c["a"]), "to": named(c["b"]), "type": c.get("type", ""), "colour": c.get("colour", ""),
               "length": c.get("length", ""), "notes": c.get("notes", "")} for c in net.get("cables", [])]

    changes = []
    for c in net.get("internet", {}).get("circuits", []):
        changes.append(f"Circuit {c.get('name', c['id'])}: new handoff and credentials from the provider ({c.get('addressing', 'unknown')}).")
    ip = net.get("internet", {}).get("public_ip", {})
    if ip.get("address"):
        changes.append(f"Public IP {ip['address']} ({ip.get('kind', 'unknown')}) will probably change.")
    ra = net.get("remote_access", {})
    for f in ra.get("port_forwards", []):
        changes.append(f"Port forward {f.get('external')}/{f.get('protocol', 'tcp')}: retest from outside; fails behind CGNAT.")
    for x in ra.get("ddns", []):
        changes.append(f"Dynamic DNS {x.get('hostname')}: confirm the updater ran.")
    for z in net.get("dns", {}).get("zones", []):
        for r in z.get("records", []):
            if r.get("depends_on_public_ip"):
                changes.append(f"DNS {r.get('type')} {r.get('name')} in {z['name']} points at the public IP: update it.")
    return {"faceplates": plates, "addresses": addresses, "cables": cables, "topology": topology(net),
            "move_changes": changes, "devices": {k: v.get("name", k) for k, v in devices.items()}}


def cmd_build(a):
    net, site = resolve_input(a)
    err, warn, gaps = validate(net, site)
    if err:
        out({"errors": err})
        sys.exit(1)
    if not shutil.which("typst"):
        sys.exit("typst not found on PATH.")
    date = a.date or dt.date.today().isoformat()
    slug = net["site"]["slug"]
    title = f"Network setup at {net['site']['name']}, {date}"
    version = load(ROOT / ".claude-plugin/plugin.json")["version"]
    build = site / ".build"
    build.mkdir(exist_ok=True)
    shutil.copy(ROOT / "templates/playbook.typ", build / "playbook.typ")
    doc = dict(net, derived=derive(net), render={"title": title, "date": date, "gaps": gaps, "footer_line": config().get("footer_line", "")})
    (build / "data.json").write_text(json.dumps(doc, ensure_ascii=False))
    releases = Path(a.out) if a.out else site / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    pdf = releases / f"Network-Playbook-{slug}-{date}.pdf"
    r = subprocess.run(["typst", "compile", "--root", str(site), str(build / "playbook.typ"), str(pdf)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    machine = dict(net)
    machine["_meta"] = {
        "title": title, "generated": date, "generator": f"{NAME} {version}", "companion_pdf": pdf.name,
        "definition_sha256": hashlib.sha256(json.dumps(net, sort_keys=True).encode()).hexdigest(),
        "readiness_gaps": gaps,
        "agent_instructions": "This is the authoritative definition of the network, written to rebuild it. Work through rebuild.phases in order, "
                              "running each step's verify check before moving on and stopping at each pause_point. Run rebuild.reconstitution last. "
                              "Fields ending in _ref name where a secret is stored; they never hold the secret. Facts carry source and last_verified: "
                              "trust live evidence over this file, and record any difference.",
    }
    js = pdf.with_suffix(".json")
    js.write_text(json.dumps(machine, indent=2, ensure_ascii=False) + "\n")
    out({"title": title, "pdf": str(pdf), "json": str(js), "warnings": warn, "readiness_gaps": gaps, "typst": r.stderr.strip()})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("path")
    i = s.add_parser("init"); i.add_argument("slug"); i.add_argument("--name")
    c = s.add_parser("scan"); c.add_argument("--site"); c.add_argument("--iface"); c.add_argument("--cidr")
    d = s.add_parser("diff"); d.add_argument("--site"); d.add_argument("--scan")
    v = s.add_parser("validate"); v.add_argument("--site"); v.add_argument("--file")
    b = s.add_parser("build"); b.add_argument("--site"); b.add_argument("--file"); b.add_argument("--date"); b.add_argument("--out")
    a = p.parse_args()
    if a.cmd == "path":
        path, rule = data_dir()
        return out({"data_dir": str(path), "rule": rule})
    {"init": cmd_init, "scan": cmd_scan, "diff": cmd_diff, "validate": cmd_validate, "build": cmd_build}[a.cmd](a)


if __name__ == "__main__":
    main()
