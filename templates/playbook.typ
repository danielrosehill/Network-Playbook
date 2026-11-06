// Network Playbook. np.py stages this next to data.json and compiles with --root at the site folder.
#import "@preview/cntopo:0.1.0": cetz, icons

#let d = json("data.json")
#let x = d.derived
#let r = d.render
#let accent = rgb("#1a5276")
#let tint = accent.lighten(88%)
#let grey = luma(110)

#set document(title: r.title)
#set page(paper: "a4", margin: (x: 1.8cm, y: 2cm), footer: context [
  #set text(8pt, fill: grey)
  #r.title #h(1fr) #counter(page).display("1 / 1", both: true)
])
#set text(font: ("IBM Plex Sans", "DejaVu Sans"), size: 9.5pt, lang: "en")
#set heading(numbering: "1.")
#show heading.where(level: 1): it => block(above: 1.4em, below: 0.7em, text(14pt, fill: accent, it))
#show heading.where(level: 2): set text(11pt)

#let g(o, k, default: "") = {
  let val = o.at(k, default: none)
  if val == none { default } else { val }
}
#let show-cell(c) = if c == none { "" } else if type(c) == str or type(c) == content { c } else { str(c) }
#let tbl(cols, heads, rows) = if rows.len() == 0 { emph[None recorded.] } else {
  table(columns: cols, inset: 4.5pt, stroke: 0.4pt + luma(170),
    fill: (_, y) => if y == 0 { tint },
    table.header(..heads.map(h => strong(h))),
    ..rows.flatten().map(show-cell))
}
#let tick = box(width: 9pt, height: 9pt, stroke: 0.7pt + black, baseline: 1pt)
#let devname(id) = x.devices.at(id, default: id)
#let note(body) = block(fill: tint, inset: 7pt, radius: 3pt, width: 100%, body)

// ---------- Cover ----------
#align(center)[
  #v(1em)
  #text(22pt, weight: "bold", fill: accent)[Network Playbook]
  #v(0.2em)
  #text(13pt)[#d.site.name]
  #v(0.1em)
  #text(10pt, fill: grey)[#g(d.site, "address") #if g(d.site, "address") != "" [·] As of #r.date]
]
#v(0.6em)
#if g(d.site, "summary") != "" { d.site.summary }

#let circuits = g(d.internet, "circuits", default: ())
#tbl((auto, 1fr), ("At a glance", ""), (
  ("Provider", g(g(d.internet, "provider", default: (:)), "name")),
  ("WAN", circuits.map(c => g(c, "name", default: c.id) + " (" + g(c, "type") + ", " + g(c, "addressing") + ")").join("; ", default: "")),
  ("Networks", d.prefixes.map(p => p.name + " " + p.cidr).join("; ", default: "")),
  ("Devices / cables", str(d.devices.len()) + " / " + str(d.cables.len())),
))

#if r.gaps.len() > 0 or d.open_questions.len() > 0 {
  v(0.5em)
  note[*Not yet complete.* This document is not ready to rely on until these are closed:
    #for q in r.gaps + d.open_questions [\ • #q]]
}
#outline(depth: 1, title: [Contents])
#pagebreak()

// ---------- Move ----------
= Moving: what to do first
Do-Confirm: work from memory, then stop and confirm every line before anything leaves the building.

#if d.rebuild.move_out.len() > 0 {
  for s in d.rebuild.move_out [#tick #h(4pt) #s \ ]
} else { emph[No move-out checks recorded.] }

== Jump kit
The minimum set that gives working internet and admin access at the new site. It travels last-out, first-in, and goes up before anything else.

#if d.rebuild.jump_kit.len() > 0 {
  for j in d.rebuild.jump_kit [#tick #h(4pt) #devname(j) \ ]
} else { emph[No jump kit recorded.] }

== What will change at a new address
#if x.move_changes.len() > 0 { for c in x.move_changes [• #c \ ] } else { emph[Nothing flagged.] }

// ---------- Rebuild ----------
= Rebuild procedure
Read-Do: read each step, do it, run its check, tick it. Do not pass a pause point until every check holds. *Bold* steps are the ones most dangerous to skip.

#for ph in d.rebuild.phases [
  == #ph.title
  #tbl((auto, auto, 1fr, 1fr), ("", "Step", "Do", "Check"), ph.steps.map(s => {
    let v = g(s, "verify", default: (:))
    let act = if g(s, "killer", default: false) { strong(s.action) } else { s.action }
    (tick, s.id, act, [#g(v, "check") #if g(v, "expected") != "" [→ #v.expected]])
  }))
  #if g(ph, "pause_point") != "" { note[*Pause point:* #ph.pause_point] }
]

== Reconstitution: declare it done only when all of these hold
#if d.rebuild.reconstitution.len() > 0 {
  for s in d.rebuild.reconstitution [#tick #h(4pt) #s \ ]
} else { emph[No reconstitution checks recorded.] }

// ---------- Topology ----------
= Topology
#let t = x.topology
#let ic = icons(fill: accent, fill-inner: white, stroke-inner: white, stroke: accent + 0.8pt, flat: true)
#align(center, cetz.canvas(length: t.unit_cm * 1cm, {
  import cetz.draw: *
  for e in t.edges {
    line((e.x1, -e.y1), (e.x2, -e.y2), stroke: 0.8pt + grey)
    if e.label != "" {
      content(((e.x1 + e.x2) / 2, -(e.y1 + e.y2) / 2), box(fill: white, inset: 1.5pt, text(6.5pt, fill: grey, e.label)))
    }
  }
  for n in t.nodes {
    (ic.at(n.icon))((n.x, -n.y), label: box(fill: white, inset: 1.5pt, text(7pt)[*#n.name* #if n.ip != "" [\ #n.ip]]))
  }
}))
#if t.unconnected.len() > 0 [Not cabled in this record: #t.unconnected.map(devname).join(", ").]

#if d.plot.len() > 0 [
  == Physical layout
  #tbl((auto, 1fr), ("Item", "Where it goes"), d.plot.map(p => (p.item, p.location)))
]

// ---------- Addressing ----------
= Addressing
#tbl((auto, auto, auto, auto, 1fr), ("Network", "CIDR", "VLAN", "Gateway", "DHCP range"), d.prefixes.map(p => (
  p.name, p.cidr, g(p, "vlan", default: "untagged"), g(p, "gateway"),
  g(p, "ip_ranges", default: ()).map(q => q.start + " – " + q.end + " on " + devname(g(q, "server"))).join("; ", default: "none"),
)))
#v(0.5em)
== IP reservations and fixed addresses
#tbl((auto, 1fr, auto, auto, auto), ("IP", "Device", "MAC", "Type", "Name"),
  x.addresses.map(a => (raw(a.ip), a.device, raw(a.mac), a.assignment, a.dns_name)))

#if d.wireless.len() > 0 [
  == Wi-Fi
  #tbl((1fr, auto, auto, 1fr), ("SSID", "Bands", "Network", "Password is in"),
    d.wireless.map(w => (w.ssid, g(w, "bands"), g(w, "prefix"), g(w, "password_ref"))))
]

// ---------- Hardware ----------
#pagebreak()
= Hardware and port maps
Every faceplate is drawn as you see it, left to right. Sockets show the printed number; the line under each is where its cable goes.

#let use-fill = (wan: rgb("#f5b7b1"), uplink: rgb("#aed6f1"), trunk: rgb("#aed6f1"), lan: rgb("#d5f5e3"), mgmt: rgb("#fdebd0"), spare: luma(235))
#let photo-of = d.photos.map(p => (p.id, p)).to-dict()
#for f in x.faceplates {
  block(breakable: false)[
    == #f.name
    #text(fill: grey)[#f.model]
    #for face in f.faces {
      block(stroke: 1.2pt + black, radius: 3pt, inset: 7pt, width: 100%)[
        #text(7.5pt, fill: grey, upper(face.face) + " · row " + str(face.row))
        #let n = if face.ports.len() > 6 { 12 } else { 6 }
        #let small = if n == 12 { 5.5pt } else { 7pt }
        #grid(columns: (1fr,) * n, column-gutter: 3pt, ..face.ports.map(p => align(center, stack(spacing: 3pt,
          text(6.5pt, weight: "bold", p.label),
          box(width: 100%, height: 17pt, radius: 1.5pt, stroke: 0.7pt + black, fill: use-fill.at(p.use, default: white),
            align(center + horizon, text(8pt, str(p.position)))),
          text(small, p.far),
          text(small, fill: grey, p.cable + if p.os_name != "" and p.cable != "" { " · " } + p.os_name),
        ))))
      ]
    }
    #if f.notes != "" { f.notes }
  ]
  for id in f.photos {
    let p = photo-of.at(id)
    figure(image("/" + p.file, width: 75%), caption: g(p, "caption"))
  }
}

// ---------- Cables ----------
#pagebreak()
= Cable schedule
One row per cable, in patch order. Each end of the cable carries its cable number.
#tbl((auto, auto, 1fr, 1fr, auto, auto, auto), ("", "Cable", "From", "To", "Type", "Colour", "Length"),
  x.cables.map(c => (tick, strong(c.id), c.from, c.to, c.type, c.colour, c.length)))

// ---------- Internet ----------
= Internet and fallback plan
#let pv = g(d.internet, "provider", default: (:))
#tbl((auto, 1fr), ("Provider", ""), (
  ("Name", g(pv, "name")), ("Support", g(pv, "support")), ("Account details are in", g(pv, "account_ref")),
))
#v(0.4em)
#tbl((auto, auto, auto, 1fr), ("Circuit", "Handoff", "Addressing", "Lands on"), circuits.map(c => (
  g(c, "name", default: c.id), g(c, "handoff"), g(c, "addressing"),
  devname(g(c, "device")) + " " + g(c, "interface") + if g(c, "credential_ref") != "" { " · credentials in " + c.credential_ref },
)))
#let pip = g(d.internet, "public_ip", default: (:))
#if g(pip, "address") != "" [Public IP #raw(pip.address) (#g(pip, "kind")), observed #g(pip, "observed").]

#let pace-table(title, plan) = [
  == #title
  #tbl((auto, 1fr, 1fr, auto), ("", "Method", "Switch when", "Last tested"), ("primary", "alternate", "contingency", "emergency").filter(k => k in plan).map(k => (
    strong(upper(k.first())), plan.at(k).method, g(plan.at(k), "switch_when"), g(plan.at(k), "last_tested", default: "never"),
  )))
]
#if "internet" in d.pace { pace-table("PACE: getting online", d.pace.internet) }
#if "admin_access" in d.pace { pace-table("PACE: reaching the admin interfaces", d.pace.admin_access) }

// ---------- Services ----------
= Servers and services
#tbl((1fr, 1fr, auto, 1fr), ("Service", "Host", "Port", "URL"),
  d.services.map(s => (s.name, devname(g(s, "host")), g(s, "port"), g(s, "url"))))
#let hosted = d.devices.filter(v => g(v, "hosted_on") != "")
#if hosted.len() > 0 [
  == Virtual machines and containers
  #tbl((1fr, 1fr, 1fr), ("Name", "Runs on", "OS"), hosted.map(v => (v.name, devname(v.hosted_on), g(v, "os"))))
]

// ---------- Remote access ----------
= Remote access
#let ra = d.remote_access
#let ts = g(ra, "tailscale", default: (:))
== Tailscale #if g(ts, "tailnet") != "" [(#ts.tailnet)]
#tbl((1fr, auto, 1fr, auto), ("Node", "IP", "Subnet routes", "Exit node"), g(ts, "nodes", default: ()).map(n => (
  n.name, raw(g(n, "ip")), g(n, "subnet_routes", default: ()).join(", ", default: ""), if g(n, "exit_node", default: false) { "yes" } else { "" },
)))
== Cloudflare tunnels
#tbl((auto, auto, 1fr, 1fr), ("Tunnel", "Runs on", "Public hostname", "Goes to"), g(ra, "cloudflare_tunnels", default: ()).map(c =>
  g(c, "routes", default: ()).map(q => (c.name, devname(g(c, "connector")), q.hostname, raw(q.service)))).flatten().chunks(4))
== Port forwards
#tbl((auto, auto, 1fr, 1fr), ("External", "Protocol", "Target", "Notes"), g(ra, "port_forwards", default: ()).map(f => (
  g(f, "external"), g(f, "protocol"), g(f, "target"), g(f, "notes"))))
#if g(ra, "ddns", default: ()).len() > 0 [
  == Dynamic DNS
  #tbl((1fr, 1fr, 1fr), ("Hostname", "Provider", "Updated by"), ra.ddns.map(f => (f.hostname, g(f, "provider"), g(f, "updater"))))
]

// ---------- DNS ----------
= DNS
#let rs = g(d.dns, "resolver", default: (:))
#if g(rs, "device") != "" [Local resolver: #devname(rs.device). Upstreams: #g(rs, "upstreams", default: ()).join(", ", default: "none recorded").]
#if g(d.dns, "overrides", default: ()).len() > 0 [
  == Local overrides
  #tbl((1fr, 1fr), ("Host", "IP"), d.dns.overrides.map(o => (o.host, raw(o.ip))))
]
#for z in g(d.dns, "zones", default: ()) [
  == #z.name
  Registrar: #g(z, "registrar"). Nameservers: #g(z, "nameservers", default: ()).join(", ", default: "not recorded").
  #tbl((auto, 1fr, 1fr, auto), ("Type", "Name", "Value", "Tied to public IP"), g(z, "records", default: ()).map(q => (
    q.type, q.name, raw(q.value), if g(q, "depends_on_public_ip", default: false) { "yes" } else { "" })))
]

// ---------- Change log ----------
#if d.changelog.len() > 0 [
  = Change log
  #tbl((auto, 1fr), ("Date", "Change"), d.changelog.map(c => (c.date, c.summary)))
]
#if r.footer_line != "" { v(1em); emph(r.footer_line) }
