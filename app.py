"""
KolkataCloud.in — Windows Managed VPS Landing Page
Python 3.14 · Flask · Jinja2
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from html import escape
from dataclasses import dataclass
from typing import Final

try:
    from flask import Flask, Response, request, jsonify
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


# ── Dataclasses ───────────────────────────────────────────────────────────────
@dataclass(slots=True)
class VPSPlan:
    name:      str
    price:     str
    period:    str
    cpu:       str
    ram:       str
    storage:   str
    bandwidth: str
    os:        str
    highlight: bool = False

    def specs(self) -> list[str]:
        return [
            self.cpu,
            self.ram,
            self.storage,
            f"Bandwidth: {self.bandwidth}",
            "1 Gbps Network Speed",
            "Full RDP Admin Access",
            "Managed Security & Backups",
            "24/7 Priority Support",
        ]


@dataclass(slots=True)
class Feature:
    svg_path: str
    title:    str
    desc:     str


# ── Data ──────────────────────────────────────────────────────────────────────

# Plans based on atozserver.com/cloud-vps — India (East) datacenter
# AE01 excluded (Linux only). AE02 / AE04 / AE08 support Windows & Linux.
VPS_PLANS: Final[list[VPSPlan]] = [
    VPSPlan("AE02", "Rs.804",   "/mo", "2 Dedicated vCPU", "4 GB RAM",  "80 GB NVMe SSD",  "2 TB", "Windows Server 2022"),
    VPSPlan("AE04", "Rs.1,693", "/mo", "4 Dedicated vCPU", "8 GB RAM",  "160 GB NVMe SSD", "3 TB", "Windows Server 2022", highlight=True),
    VPSPlan("AE08", "Rs.3,520", "/mo", "8 Dedicated vCPU", "16 GB RAM", "240 GB NVMe SSD", "4 TB", "Windows Server 2022"),
]

FEATURES: Final[list[Feature]] = [
    Feature("M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v10m0 0h10M9 13H5a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2v-4a2 2 0 00-2-2zm10 0h-4",
            "Full RDP Access", "Remote Desktop Protocol with full administrator privileges. Manage your server exactly like a local Windows machine, from anywhere."),
    Feature("M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
            "Managed Security", "Enterprise DDoS protection, automated firewall rules, and continuous 24/7 threat monitoring with zero configuration required."),
    Feature("M13 10V3L4 14h7v7l9-11h-7z",
            "NVMe SSD Storage", "Gen 4 NVMe SSDs delivering up to 7,000 MB/s sequential read speeds, 5x faster than conventional SATA SSDs."),
    Feature("M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
            "Automated Backups", "Daily snapshots with 7-day rolling retention. Point-in-time recovery available for all plans with a single click."),
    Feature("M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z",
            "24/7 Expert Support", "Kolkata-based engineers available around the clock via phone, live chat, and a dedicated support portal."),
    Feature("M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
            "India (East) Network", "Tier-III data centre in India (East) with redundant 1 Gbps uplinks, ensuring sub-5 ms latency for all domestic traffic."),
]

OS_SPECS: Final[list[tuple[str, str]]] = [
    ("Kernel Build",     "NT 10.0 (Build 20348)"),
    ("Architecture",     "x86_64  64-bit"),
    ("Remote Access",    "RDP 3389 / WinRM / SSH"),
    ("Web Server",       "IIS 10.0 included"),
    (".NET Runtime",     "Up to .NET 8 / ASP.NET"),
    ("Security Suite",   "Defender + Windows Firewall"),
    ("Patch Management", "Managed by KolkataCloud"),
    ("License",          "Genuine Microsoft License"),
]

USE_CASES: Final[list[tuple[str, str, str]]] = [
    ("M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4",
     "ASP.NET &amp; IIS Web Hosting",
     "Deploy .NET 6/7/8 or legacy WebForms apps on IIS with full administrator control"),
    ("M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7M4 7c0-2 1-3 3-3h10c2 0 3 1 3 3M4 7h16",
     "SQL Server &amp; Database Workloads",
     "Run MSSQL, MySQL or PostgreSQL on high-IOPS NVMe with automated zero-effort backups"),
    ("M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
     "Remote Desktop &amp; GUI Applications",
     "Access a full Windows desktop environment via RDP from any device, anywhere in the world"),
    ("M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z",
     "Active Directory &amp; Group Policy",
     "Provision AD DS, DNS, DHCP, and GPO for secure multi-user enterprise environments"),
]

TRUST_ITEMS: Final[list[str]] = [
    "India (East) Data Centre",
    "99.9% Uptime SLA",
    "Windows Server 2022",
    "AMD EPYC + DDR5 RAM",
    "1 Gbps Network Speed",
    "No Hidden Fees",
]

# ── Contact details — update these ────────────────────────────────────────────
SALES_EMAIL   = "sales@kolkatacloud.in"
ENQUIRY_EMAIL = "sales@kolkatacloud.in"
SUPPORT_PHONE = "+91-8653436887"           # FIX 1: replace with real number
SUPPORT_WA    = "https://wa.me/8653436887"  # FIX 1: uncommented — replace with real WhatsApp link

# ── SMTP config — update before deploying ─────────────────────────────────────
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "softwaresomenath002@gmail.com"
SMTP_PASS = "aibo tjgr xhat fswn"


# ── Helper ────────────────────────────────────────────────────────────────────
def e(text: str) -> str:
    return escape(str(text), quote=True)


# ── Renderer ──────────────────────────────────────────────────────────────────
def render_page() -> str:
    year       = datetime.now().year
    py_ver     = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    feature_cards = "\n".join(
        f'    <div class="fc"><div class="fic"><svg width="19" height="19" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="{e(f.svg_path)}"/></svg></div><div class="ft">{e(f.title)}</div><p class="fd">{e(f.desc)}</p></div>'
        for f in FEATURES
    )

    def plan_card(p: VPSPlan) -> str:
        tag   = '<div class="ptag">Most Popular</div>' if p.highlight else ""
        cls   = "plan ft2" if p.highlight else "plan"
        cta_c = "pcta-wh" if p.highlight else "pcta-ol"
        cta_l = "Get Started &rarr;" if p.highlight else "Choose Plan"
        items = "\n".join(
            f'<li class="ps"><span class="pck"><svg width="8" height="8" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg></span><strong>{e(s)}</strong></li>'
            for s in p.specs()
        )
        return f'<div class="{cls}">{tag}<div class="ptier">{e(p.name)}</div><div class="ppr">{e(p.price)}</div><div class="pper">per month, billed monthly</div><div class="postag">{e(p.os)}</div><div class="pdiv"></div><ul class="pspecs">{items}</ul><a href="#contact" class="pcta {cta_c}">{cta_l}</a></div>'

    pricing_cards = "\n".join(plan_card(p) for p in VPS_PLANS)

    os_rows = "\n".join(
        f'<div class="osrow"><span class="osk">{e(k)}</span><span class="osv">{e(v)}</span></div>'
        for k, v in OS_SPECS
    )

    use_items = "\n".join(
        f'<li class="ui"><span class="uico"><svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="{e(svg)}"/></svg></span><div><div class="ut">{title}</div><div class="us">{e(desc)}</div></div></li>'
        for svg, title, desc in USE_CASES
    )

    trust_html = "\n".join(
        f'<div class="ti"><svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>{e(t)}</div>'
        for t in TRUST_ITEMS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Windows Managed VPS India | KolkataCloud.in</title>
<meta name="description" content="Premium Windows Managed VPS in India. RDP, NVMe SSD, 24/7 support. Plans from Rs.804/mo. Email: sales@kolkatacloud.in">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}}
:root{{
  --ink:#0b0d11;--ink2:#1a1d24;--white:#fff;--off:#f8f9fb;
  --line:#e4e6eb;--line2:#f0f1f5;--muted:#6b7280;--muted2:#9ca3af;
  --blue:#1d6fe8;--bluedk:#1558c0;--bluelt:#e8f0fd;
  --green:#059669;--amber:#d97706;
  --font:'Plus Jakarta Sans',sans-serif;--mono:'JetBrains Mono',monospace;
  --r:10px;
  --sm:0 1px 3px rgba(0,0,0,.08);
  --md:0 4px 16px rgba(0,0,0,.09);
  --lg:0 12px 40px rgba(0,0,0,.12);
  --sblu:0 8px 30px rgba(29,111,232,.28);
}}
body{{background:var(--white);color:var(--ink2);font-family:var(--font);font-size:16px;line-height:1.65;overflow-x:hidden}}
.topbar{{background:var(--ink);text-align:center;padding:.55rem 5%;font-size:.78rem;color:#9ca3af}}
.topbar strong{{color:#e5e7eb}}.topbar a{{color:var(--blue);text-decoration:none}}
nav{{position:sticky;top:0;z-index:200;display:flex;align-items:center;justify-content:space-between;padding:0 5%;height:64px;background:rgba(255,255,255,.97);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}}
.logo{{font:800 1.1rem/1 var(--font);color:var(--ink);text-decoration:none;letter-spacing:-.035em;display:flex;align-items:center;gap:.3rem}}
.logo em{{display:inline-block;width:7px;height:7px;background:var(--blue);border-radius:50%;margin-bottom:2px;font-style:normal}}
.navlinks{{display:flex;gap:.15rem;list-style:none}}
.navlinks a{{color:var(--muted);text-decoration:none;font-weight:500;font-size:.87rem;padding:.42rem .85rem;border-radius:8px;transition:color .15s,background .15s}}
.navlinks a:hover{{color:var(--ink);background:var(--line2)}}
.navr{{display:flex;gap:.65rem}}
.btn-ol{{font:500 .87rem/1 var(--font);color:var(--ink);border:1.5px solid var(--line);background:transparent;padding:.5rem 1.1rem;border-radius:var(--r);text-decoration:none;transition:border-color .15s,background .15s}}
.btn-ol:hover{{border-color:var(--blue);background:var(--bluelt)}}
.btn-nv{{font:600 .87rem/1 var(--font);color:#fff;background:var(--blue);border:none;padding:.55rem 1.3rem;border-radius:var(--r);text-decoration:none;transition:background .15s,transform .1s}}
.btn-nv:hover{{background:var(--bluedk);transform:translateY(-1px)}}
/* hero */
.hero{{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;padding:88px 5% 72px;background:var(--ink);min-height:92vh;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:-120px;right:-80px;width:600px;height:600px;background:radial-gradient(circle at 60% 40%,rgba(29,111,232,.22) 0%,transparent 65%);pointer-events:none}}
.hero-l{{position:relative;z-index:1}}
.hero-eyebrow{{display:inline-flex;align-items:center;gap:.55rem;font:600 .7rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:1.5rem}}
.hero-eyebrow span{{display:block;width:26px;height:1.5px;background:var(--blue)}}
h1{{font-size:clamp(2.3rem,4vw,3.6rem);font-weight:800;line-height:1.07;letter-spacing:-.045em;color:#fff;margin-bottom:1.25rem}}
h1 .hl{{background:linear-gradient(90deg,#5aabff,#38d4f0);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero-p{{font-size:1.02rem;color:rgba(255,255,255,.52);line-height:1.75;max-width:480px;margin-bottom:2.25rem}}
.hero-btns{{display:flex;gap:.8rem;flex-wrap:wrap;margin-bottom:3rem}}
.btn-hero{{font:600 .93rem/1 var(--font);color:#fff;background:var(--blue);border:none;padding:.8rem 1.8rem;border-radius:var(--r);text-decoration:none;box-shadow:var(--sblu);transition:background .15s,transform .1s}}
.btn-hero:hover{{background:var(--bluedk);transform:translateY(-2px)}}
.btn-ghost{{font:500 .93rem/1 var(--font);color:rgba(255,255,255,.68);background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.12);padding:.8rem 1.8rem;border-radius:var(--r);text-decoration:none;transition:background .15s}}
.btn-ghost:hover{{background:rgba(255,255,255,.13);color:#fff}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid rgba(255,255,255,.09);border-radius:var(--r);overflow:hidden}}
.metric{{padding:1.2rem 1rem;border-right:1px solid rgba(255,255,255,.09);text-align:center}}
.metric:last-child{{border-right:none}}
.mval{{font:800 1.75rem/1 var(--font);letter-spacing:-.045em;color:#fff;margin-bottom:.3rem}}
.mval sub{{font-size:.9rem;font-weight:600}}
.mlbl{{font-size:.71rem;font-weight:500;color:rgba(255,255,255,.38);letter-spacing:.04em;text-transform:uppercase}}
.hero-r{{position:relative;z-index:1}}
/* terminal */
.terminal{{background:#0d1117;border:1px solid rgba(255,255,255,.1);border-radius:14px;overflow:hidden;box-shadow:var(--lg);font-family:var(--mono)}}
.tbar{{display:flex;align-items:center;gap:.45rem;padding:.75rem 1rem;background:#161b22;border-bottom:1px solid rgba(255,255,255,.07)}}
.td{{width:11px;height:11px;border-radius:50%}}
.td.r{{background:#ff5f57}}.td.y{{background:#febc2e}}.td.g{{background:#28c840}}
.ttitle{{font-size:.73rem;color:rgba(255,255,255,.3);margin:0 auto}}
.tbody{{padding:1.2rem 1.2rem 1.5rem;font-size:.78rem;line-height:1.85}}
.tl{{margin-bottom:.1rem}}
.cm{{color:rgba(255,255,255,.25)}}.cp{{color:#28c840}}.cc{{color:#79b8ff}}
.ck{{color:#ffab70}}.cv{{color:#9ecbff}}.cs{{color:#85e89d}}
.cco{{color:rgba(255,255,255,.23);font-style:italic}}.csc{{color:#d2a8ff;font-weight:500}}.cw{{color:#febc2e}}
.cursor{{display:inline-block;width:7px;height:13px;background:#28c840;vertical-align:middle;animation:blink 1.1s step-end infinite;margin-left:2px}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
/* trust */
.trust{{background:var(--line2);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:center;gap:2.5rem;padding:1rem 5%;flex-wrap:wrap}}
.ti{{display:flex;align-items:center;gap:.5rem;font-size:.8rem;font-weight:600;color:var(--muted);white-space:nowrap}}
.ti svg{{color:var(--blue);flex-shrink:0}}
/* sections */
section{{padding:80px 5%}}
.slbl{{display:inline-flex;align-items:center;gap:.5rem;font:600 .7rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:var(--blue);margin-bottom:.85rem}}
.slbl::before{{content:'';display:block;width:20px;height:1.5px;background:var(--blue)}}
.stitle{{font-size:clamp(1.7rem,3vw,2.4rem);font-weight:800;letter-spacing:-.038em;line-height:1.12;color:var(--ink)}}
.sdesc{{font-size:.95rem;color:var(--muted);max-width:520px;margin-top:.55rem;line-height:1.72}}
.sh{{margin-bottom:2.75rem}}.csh{{text-align:center}}.csh .sdesc{{margin:.55rem auto 0}}
/* features */
#features{{background:var(--white)}}
.fgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.15rem}}
.fc{{background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:1.65rem;transition:border-color .2s,box-shadow .2s,transform .2s}}
.fc:hover{{border-color:var(--blue);box-shadow:var(--md);transform:translateY(-3px)}}
.fic{{width:42px;height:42px;border-radius:10px;background:var(--bluelt);display:flex;align-items:center;justify-content:center;margin-bottom:1rem;color:var(--blue)}}
.ft{{font-size:.95rem;font-weight:700;color:var(--ink);margin-bottom:.45rem}}
.fd{{font-size:.85rem;color:var(--muted);line-height:1.72}}
/* pricing */
#pricing{{background:var(--ink2)}}
#pricing .stitle{{color:#fff}}#pricing .sdesc{{color:rgba(255,255,255,.42)}}
.pgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.15rem;max-width:1060px;margin:0 auto}}
.plan{{background:#fff;border-radius:16px;padding:2rem 1.75rem;position:relative;box-shadow:var(--md);display:flex;flex-direction:column;transition:transform .2s,box-shadow .2s}}
.plan:hover{{transform:translateY(-4px);box-shadow:var(--lg)}}
.plan.ft2{{background:var(--blue);transform:translateY(-8px);box-shadow:0 20px 60px rgba(29,111,232,.42)}}
.plan.ft2:hover{{transform:translateY(-12px)}}
.ptag{{position:absolute;top:-13px;left:50%;transform:translateX(-50%);background:var(--amber);color:#fff;font:700 .67rem/1 var(--font);letter-spacing:.08em;text-transform:uppercase;padding:.28rem .85rem;border-radius:100px;white-space:nowrap}}
.ptier{{font:700 .68rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:var(--muted2);margin-bottom:.8rem}}
.plan.ft2 .ptier{{color:rgba(255,255,255,.6)}}
.ppr{{font:800 2.5rem/1 var(--font);letter-spacing:-.05em;color:var(--ink)}}
.plan.ft2 .ppr{{color:#fff}}
.pper{{font-size:.87rem;color:var(--muted)}}.plan.ft2 .pper{{color:rgba(255,255,255,.58)}}
.postag{{display:inline-block;margin:1rem 0;font:500 .7rem/1 var(--mono);background:rgba(29,111,232,.07);color:var(--blue);border:1px solid rgba(29,111,232,.18);border-radius:6px;padding:.28rem .6rem}}
.plan.ft2 .postag{{background:rgba(255,255,255,.14);color:#fff;border-color:rgba(255,255,255,.28)}}
.pdiv{{height:1px;background:var(--line);margin:.4rem 0 1.2rem}}.plan.ft2 .pdiv{{background:rgba(255,255,255,.2)}}
.pspecs{{list-style:none;flex:1;margin-bottom:1.65rem}}
.ps{{display:flex;align-items:center;gap:.6rem;font-size:.862rem;padding:.42rem 0;color:var(--muted);border-bottom:1px solid var(--line2)}}
.plan.ft2 .ps{{color:rgba(255,255,255,.78);border-color:rgba(255,255,255,.12)}}
.ps:last-child{{border-bottom:none}}
.ps strong{{color:var(--ink);font-weight:600}}.plan.ft2 .ps strong{{color:#fff}}
.pck{{width:15px;height:15px;border-radius:50%;background:rgba(5,150,105,.1);display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;color:var(--green)}}
.plan.ft2 .pck{{background:rgba(255,255,255,.2);color:#fff}}
.pcta{{display:block;text-align:center;text-decoration:none;padding:.82rem;border-radius:10px;font:600 .88rem/1 var(--font);transition:all .15s}}
.pcta-ol{{background:transparent;color:var(--blue);border:1.5px solid var(--line)}}.pcta-ol:hover{{border-color:var(--blue);background:var(--bluelt)}}
.pcta-wh{{background:#fff;color:var(--blue);border:none;box-shadow:0 2px 8px rgba(0,0,0,.14)}}.pcta-wh:hover{{background:#f0f6ff}}
/* OS */
#os-info{{background:var(--off)}}
.osgrid{{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;max-width:1100px;margin:0 auto}}
.oscard{{background:#fff;border:1.5px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--md)}}
.oschd{{background:var(--ink);color:#fff;padding:1.4rem 1.65rem;display:flex;align-items:center;gap:1rem}}
.winico{{width:46px;height:46px;background:linear-gradient(135deg,#0078d4,#00a8e0);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.oscht{{font:700 .97rem/1.2 var(--font)}}.oschs{{font-size:.76rem;color:rgba(255,255,255,.45);margin-top:.2rem}}
.osrow{{display:flex;justify-content:space-between;align-items:center;padding:.82rem 1.65rem;border-bottom:1px solid var(--line);font-size:.86rem}}
.osrow:last-child{{border-bottom:none}}
.osk{{color:var(--muted);font-weight:500}}.osv{{color:var(--ink);font-weight:600;font-family:var(--mono);font-size:.78rem}}
.osdet h3{{font:800 1.85rem/1.1 var(--font);letter-spacing:-.038em;color:var(--ink);margin-bottom:1rem}}
.osdet p{{font-size:.92rem;color:var(--muted);line-height:1.75;margin-bottom:1.5rem}}
.ulist{{list-style:none;display:flex;flex-direction:column;gap:.8rem}}
.ui{{display:flex;align-items:flex-start;gap:.8rem;padding:.85rem .95rem;background:#fff;border:1.5px solid var(--line);border-radius:10px;transition:border-color .15s}}
.ui:hover{{border-color:var(--blue)}}
.uico{{width:31px;height:31px;border-radius:7px;background:var(--bluelt);color:var(--blue);display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.ut{{font:600 .86rem/1 var(--font);color:var(--ink);margin-bottom:.24rem}}.us{{font-size:.78rem;color:var(--muted);line-height:1.55}}
/* contact */
#contact{{background:var(--ink2);padding:80px 5%}}
#contact .stitle{{color:#fff}}#contact .sdesc{{color:rgba(255,255,255,.42)}}
.contact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:3rem;max-width:1060px;margin:0 auto;align-items:start}}
.contact-info{{display:flex;flex-direction:column;gap:1.4rem}}
.cinfo-card{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:1.3rem 1.5rem;display:flex;align-items:flex-start;gap:1rem;transition:border-color .2s,background .2s}}
.cinfo-card:hover{{border-color:var(--blue);background:rgba(29,111,232,.08)}}
.cinfo-ico{{width:42px;height:42px;border-radius:10px;background:var(--blue);display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#fff}}
.cinfo-label{{font:700 .7rem/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.35);margin-bottom:.4rem}}
.cinfo-value{{font:600 .95rem/1.35 var(--font);color:#fff}}
.cinfo-value a{{color:#fff;text-decoration:none;transition:color .15s}}.cinfo-value a:hover{{color:#5aabff}}
.cinfo-sub{{font-size:.77rem;color:rgba(255,255,255,.32);margin-top:.2rem}}
/* enquiry form */
.enquiry-form{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:2rem}}
.form-title{{font:700 1.05rem/1 var(--font);color:#fff;margin-bottom:1.4rem;display:flex;align-items:center;gap:.5rem}}
.form-title svg{{color:var(--blue)}}
.frow{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}}
.frow.full{{grid-template-columns:1fr}}
.fgroup{{display:flex;flex-direction:column;gap:.38rem}}
.fgroup label{{font:600 .7rem/1 var(--font);letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.4)}}
.fgroup input,.fgroup select,.fgroup textarea{{width:100%;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:.7rem .95rem;font:500 .9rem/1 var(--font);color:#fff;outline:none;transition:border-color .15s,background .15s;-webkit-appearance:none}}
.fgroup select option{{background:var(--ink2);color:#fff}}
.fgroup textarea{{resize:vertical;min-height:110px;line-height:1.6}}
.fgroup input::placeholder,.fgroup textarea::placeholder{{color:rgba(255,255,255,.22)}}
.fgroup input:focus,.fgroup select:focus,.fgroup textarea:focus{{border-color:var(--blue);background:rgba(29,111,232,.08)}}
.form-submit{{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-top:1.4rem;flex-wrap:wrap}}
.btn-submit{{font:600 .92rem/1 var(--font);color:#fff;background:var(--blue);border:none;padding:.85rem 2rem;border-radius:var(--r);cursor:pointer;transition:background .15s,transform .1s,box-shadow .15s;display:flex;align-items:center;gap:.5rem}}
.btn-submit:hover{{background:var(--bluedk);transform:translateY(-1px);box-shadow:var(--sblu)}}
.form-note{{font-size:.75rem;color:rgba(255,255,255,.28)}}
.form-msg{{display:none;margin-top:1rem;padding:.8rem 1rem;border-radius:8px;font:500 .87rem/1.4 var(--font)}}
.form-msg.ok{{background:rgba(5,150,105,.15);border:1px solid rgba(5,150,105,.3);color:#6ee7b7;display:block}}
.form-msg.err{{background:rgba(220,38,38,.12);border:1px solid rgba(220,38,38,.3);color:#fca5a5;display:block}}
/* footer */
footer{{background:var(--ink);color:rgba(255,255,255,.32);padding:2rem 5%;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;font-size:.78rem}}
.flogo{{font:800 1rem/1 var(--font);color:#fff;text-decoration:none;letter-spacing:-.03em}}
.flogo span{{color:var(--blue)}}
.flinks{{display:flex;gap:1.5rem}}
.flinks a{{color:rgba(255,255,255,.32);text-decoration:none;transition:color .15s}}.flinks a:hover{{color:rgba(255,255,255,.8)}}
.pybadge{{display:flex;align-items:center;gap:.4rem;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:6px;padding:.28rem .7rem;font-family:var(--mono);font-size:.7rem;color:rgba(255,255,255,.4)}}
.pydot{{width:5px;height:5px;border-radius:50%;background:#f7c948;flex-shrink:0}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.a1{{animation:fadeUp .55s .05s ease both}}.a2{{animation:fadeUp .55s .15s ease both}}
.a3{{animation:fadeUp .55s .25s ease both}}.a4{{animation:fadeUp .55s .35s ease both}}
.a5{{animation:fadeUp .55s .45s ease both}}
@media(max-width:1024px){{.fgrid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:900px){{
  .hero{{grid-template-columns:1fr;gap:2.5rem;min-height:auto;padding-bottom:56px}}
  .hero-r{{display:none}}
  .pgrid,.contact-grid{{grid-template-columns:1fr;max-width:480px;margin:0 auto}}
  .plan.ft2{{transform:none}}.osgrid{{grid-template-columns:1fr}}
  .frow{{grid-template-columns:1fr}}
}}
@media(max-width:640px){{
  nav .navlinks{{display:none}}
  .fgrid{{grid-template-columns:1fr}}
  .metrics{{grid-template-columns:repeat(2,1fr)}}
  .metric:nth-child(2){{border-right:none}}
  .metric:nth-child(3),.metric:nth-child(4){{border-top:1px solid rgba(255,255,255,.09)}}
  footer{{flex-direction:column;text-align:center}}.flinks{{justify-content:center}}
}}
</style>
</head>
<body>

<div class="topbar">
  <strong>Limited Offer:</strong> Get 2 months free on any annual plan &mdash;
  <a href="#pricing">See Plans &rarr;</a>
</div>

<nav>
  <a href="#" class="logo">KolkataCloud<em></em>in</a>
  <ul class="navlinks">
    <li><a href="#features">Features</a></li>
    <li><a href="#pricing">Pricing</a></li>
    <li><a href="#os-info">Windows VPS</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
  <div class="navr">
    <a href="mailto:{SALES_EMAIL}" class="btn-ol">Client Login</a>
    <a href="#pricing" class="btn-nv">Get Started</a>
  </div>
</nav>

<!-- HERO -->
<section class="hero" id="home">
  <div class="hero-l">
    <div class="hero-eyebrow a1"><span></span>Windows Managed VPS &mdash; India</div>
    <h1 class="a2">Enterprise Cloud<br>Infrastructure<br><span class="hl">Built for India</span></h1>
    <p class="hero-p a3">Fully managed Windows Server VPS with RDP access, NVMe SSD storage,
    and round-the-clock support &mdash; hosted in an Indian Tier-III data centre for ultra-low latency.</p>
    <div class="hero-btns a4">
      <a href="#pricing" class="btn-hero">View Plans &amp; Pricing</a>
      <a href="#contact" class="btn-ghost">Get in Touch</a>
    </div>
    <div class="metrics a5">
      <div class="metric"><div class="mval">99<sub>.9%</sub></div><div class="mlbl">Uptime SLA</div></div>
      <div class="metric"><div class="mval"><sub>Rs.</sub>804</div><div class="mlbl">Starting /mo</div></div>
      <div class="metric"><div class="mval">24<sub>/7</sub></div><div class="mlbl">Expert Support</div></div>
      <div class="metric"><div class="mval">&lt;5<sub>ms</sub></div><div class="mlbl">Local Latency</div></div>
    </div>
  </div>

  <div class="hero-r a3">
    <div class="terminal">
      <div class="tbar">
        <span class="td r"></span><span class="td y"></span><span class="td g"></span>
        <span class="ttitle">Python {py_ver} &mdash; KolkataCloud VPS Manager</span>
      </div>
      <div class="tbody">
        <div class="tl"><span class="cco"># KolkataCloud.in &mdash; Windows VPS Manager</span></div>
        <div class="tl">&nbsp;</div>
        <div class="tl"><span class="cp">&gt;&gt;&gt;</span> <span class="cc">import</span> <span class="cv">kolkatacloud</span> <span class="cc">as</span> <span class="cv">kc</span></div>
        <div class="tl"><span class="cp">&gt;&gt;&gt;</span> <span class="cv">vps</span> <span class="cm">=</span> <span class="cv">kc</span><span class="cm">.</span><span class="cc">VPS</span><span class="cm">(</span><span class="cs">"AE04"</span><span class="cm">)</span></div>
        <div class="tl">&nbsp;</div>
        <div class="tl"><span class="cp">&gt;&gt;&gt;</span> <span class="cc">print</span><span class="cm">(</span><span class="cv">vps</span><span class="cm">.</span><span class="cc">info</span><span class="cm">())</span></div>
        <div class="tl"><span class="csc">VPSInfo</span><span class="cm">(</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">plan</span>    <span class="cm">=</span> <span class="cs">'AE04'</span><span class="cm">,</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">os</span>      <span class="cm">=</span> <span class="cs">'Windows Server 2022'</span><span class="cm">,</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">cpu</span>     <span class="cm">=</span> <span class="cs">'4 Dedicated vCPU'</span><span class="cm">,</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">ram</span>     <span class="cm">=</span> <span class="cs">'8 GB DDR5'</span><span class="cm">,</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">storage</span> <span class="cm">=</span> <span class="cs">'160 GB NVMe'</span><span class="cm">,</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">latency</span> <span class="cm">=</span> <span class="cw">'3 ms'</span><span class="cm">,</span></div>
        <div class="tl">&nbsp;&nbsp;<span class="ck">status</span>  <span class="cm">=</span> <span class="cs">'running'</span></div>
        <div class="tl"><span class="cm">)</span></div>
        <div class="tl">&nbsp;</div>
        <div class="tl"><span class="cp">&gt;&gt;&gt;</span> <span class="cv">vps</span><span class="cm">.</span><span class="cc">ping</span><span class="cm">()</span></div>
        <div class="tl"><span class="cs">PingResult</span><span class="cm">(</span><span class="ck">success</span><span class="cm">=</span><span class="cw">True</span><span class="cm">,</span> <span class="ck">rtt_ms</span><span class="cm">=</span><span class="cw">3.1</span><span class="cm">)</span></div>
        <div class="tl">&nbsp;</div>
        <div class="tl"><span class="cp">&gt;&gt;&gt;</span> <span class="cursor"></span></div>
      </div>
    </div>
  </div>
</section>

<div class="trust">{trust_html}</div>

<!-- FEATURES -->
<section id="features">
  <div class="sh csh">
    <div class="slbl">Included in every plan</div>
    <h2 class="stitle">Everything you need, fully managed</h2>
    <p class="sdesc">All enterprise features bundled at no extra cost &mdash; focus on your work, not your infrastructure.</p>
  </div>
  <div class="fgrid">{feature_cards}</div>
</section>

<!-- PRICING -->
<section id="pricing">
  <div class="sh csh">
    <div class="slbl" style="color:rgba(255,255,255,.45)"><span style="background:rgba(255,255,255,.3);display:block;width:20px;height:1.5px"></span>Transparent pricing</div>
    <h2 class="stitle">Simple plans, no surprises</h2>
    <p class="sdesc">All plans include managed support, automated backups, and full RDP access. Powered by AMD EPYC&trade; &amp; DDR5 RAM.</p>
  </div>
  <div class="pgrid">{pricing_cards}</div>
</section>

<!-- OS INFO -->
<section id="os-info">
  <div class="osgrid">
    <div class="oscard">
      <div class="oschd">
        <div class="winico">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
            <path d="M3 5.557L10.325 4.5V11.44H3V5.557zM11.12 4.388L21 3V11.38H11.12V4.388zM3 12.56H10.325V19.5L3 18.443V12.56zM11.12 12.62H21V21L11.12 19.612V12.62z"/>
          </svg>
        </div>
        <div><div class="oscht">Windows Server 2022</div><div class="oschs">Standard Edition &mdash; 64-bit</div></div>
      </div>
      {os_rows}
    </div>
    <div class="osdet">
      <div class="slbl">Platform</div>
      <h3>Why Windows Server 2022?</h3>
      <p>Windows Server 2022 delivers secured-core server capabilities, hybrid cloud integration, and native container support &mdash; all within a full GUI environment. Our team handles every patch cycle so you never touch a WSUS console.</p>
      <ul class="ulist">{use_items}</ul>
    </div>
  </div>
</section>

<!-- CONTACT & ENQUIRY -->
<section id="contact">
  <div class="sh csh">
    <div class="slbl" style="color:rgba(255,255,255,.45)"><span style="background:rgba(255,255,255,.3);display:block;width:20px;height:1.5px"></span>Get in touch</div>
    <h2 class="stitle">Contact &amp; Enquiry</h2>
    <p class="sdesc">Reach our Kolkata-based team via email, WhatsApp, or fill the form and we&rsquo;ll reply within 2 hours.</p>
  </div>

  <div class="contact-grid">

    <div class="contact-info">

      <div class="cinfo-card">
        <div class="cinfo-ico">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <div>
          <div class="cinfo-label">Sales</div>
          <div class="cinfo-value"><a href="mailto:{SALES_EMAIL}">{SALES_EMAIL}</a></div>
          <div class="cinfo-sub">New plans, upgrades &amp; billing</div>
        </div>
      </div>

      <div class="cinfo-card">
        <div class="cinfo-ico">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
          </svg>
        </div>
        <div>
          <div class="cinfo-label">General Enquiry</div>
          <div class="cinfo-value"><a href="mailto:{ENQUIRY_EMAIL}">{ENQUIRY_EMAIL}</a></div>
          <div class="cinfo-sub">Technical questions &amp; support</div>
        </div>
      </div>

      <div class="cinfo-card">
        <div class="cinfo-ico">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
          </svg>
        </div>
        <div>
          <div class="cinfo-label">Phone / WhatsApp</div>
          <div class="cinfo-value"><a href="{SUPPORT_WA}">{SUPPORT_PHONE}</a></div>
          <div class="cinfo-sub">Mon &ndash; Sat &nbsp;9 AM &ndash; 8 PM IST</div>
        </div>
      </div>

      <div class="cinfo-card">
        <div class="cinfo-ico">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <div>
          <div class="cinfo-label">Office</div>
          <div class="cinfo-value">Kolkata, West Bengal, India</div>
          <div class="cinfo-sub">India (East) datacenter &mdash; ultra-low latency</div>
        </div>
      </div>

    </div>

    <!-- Enquiry form -->
    <div class="enquiry-form">
      <div class="form-title">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
        </svg>
        Send us an Enquiry
      </div>

      <div class="frow">
        <div class="fgroup">
          <label for="f-name">Your Name *</label>
          <input id="f-name" type="text" placeholder="Rajan Sharma" required>
        </div>
        <div class="fgroup">
          <label for="f-phone">Phone / WhatsApp *</label>
          <input id="f-phone" type="tel" placeholder="+91 98765 43210" required>
        </div>
      </div>

      <div class="frow">
        <div class="fgroup">
          <label for="f-email">Email Address *</label>
          <input id="f-email" type="email" placeholder="you@company.com" required>
        </div>
        <div class="fgroup">
          <label for="f-plan">Interested Plan</label>
          <select id="f-plan">
            <option value="">-- Select a plan --</option>
            <option value="AE02">AE02 &mdash; Rs.804/mo &nbsp;(4 GB RAM)</option>
            <option value="AE04">AE04 &mdash; Rs.1,693/mo &nbsp;(8 GB RAM) &#9733; Popular</option>
            <option value="AE08">AE08 &mdash; Rs.3,520/mo &nbsp;(16 GB RAM)</option>
            <option value="custom">Custom / Enterprise</option>
          </select>
        </div>
      </div>

      <div class="frow full">
        <div class="fgroup">
          <label for="f-msg">Message / Requirements</label>
          <textarea id="f-msg" placeholder="Tell us your use case — Tally hosting, web app, ERP, trading software, etc."></textarea>
        </div>
      </div>

      <div class="form-submit">
        <button class="btn-submit" onclick="submitEnquiry()">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          Send Enquiry
        </button>
        <span class="form-note">We reply within 2 business hours</span>
      </div>

      <div class="form-msg" id="form-msg"></div>
    </div>

  </div>
</section>

<!-- FOOTER -->
<footer>
  <a href="#" class="flogo">KolkataCloud<span>.in</span></a>
  <nav class="flinks">
    <a href="#features">Features</a>
    <a href="#pricing">Pricing</a>
    <a href="#os-info">Windows VPS</a>
    <a href="mailto:{SALES_EMAIL}">Sales</a>
    <a href="mailto:{ENQUIRY_EMAIL}">Enquiry</a>
  </nav>
  <p>&copy; {year} KolkataCloud.in &mdash; All rights reserved.</p>
  <div class="pybadge"><span class="pydot"></span>Python {py_ver}</div>
</footer>

<script>
function submitEnquiry() {{
  const name  = document.getElementById('f-name').value.trim();
  const phone = document.getElementById('f-phone').value.trim();
  const email = document.getElementById('f-email').value.trim();
  const plan  = document.getElementById('f-plan').value;
  const msg   = document.getElementById('f-msg').value.trim();
  const out   = document.getElementById('form-msg');

  out.className = 'form-msg';
  out.textContent = '';

  if (!name || !phone || !email) {{
    out.textContent = 'Please fill in Name, Phone, and Email before submitting.';
    out.className = 'form-msg err';
    return;
  }}

  fetch('/enquiry', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{name, phone, email, plan, message: msg}})
  }})
  .then(r => r.json())
  .then(data => {{
    if (data.ok) {{
      out.textContent = 'Enquiry sent! Our team will contact you within 2 hours.';
      out.className = 'form-msg ok';
      ['f-name','f-phone','f-email','f-msg'].forEach(id => document.getElementById(id).value = '');
      document.getElementById('f-plan').selectedIndex = 0;
    }} else {{ throw new Error(data.error || 'Server error'); }}
  }})
  .catch(() => {{
    const subject = encodeURIComponent('VPS Enquiry from ' + name + ' - ' + (plan || 'General'));
    const body    = encodeURIComponent('Name: '+name+'\\nPhone: '+phone+'\\nEmail: '+email+'\\nPlan: '+(plan||'Not selected')+'\\n\\nMessage:\\n'+msg);
    window.location.href = 'mailto:{ENQUIRY_EMAIL}?subject='+subject+'&body='+body;
    out.textContent = 'Opening your mail client... If nothing opens, email us at {ENQUIRY_EMAIL}';
    out.className = 'form-msg ok';
  }});
}}
</script>
</body>
</html>"""


# ── Flask app ─────────────────────────────────────────────────────────────────
def create_flask_app():
    if not HAS_FLASK:
        return None

    app = Flask(__name__)

    @app.route("/")
    def index() -> Response:
        return Response(render_page(), mimetype="text/html")

    @app.route("/enquiry", methods=["POST"])
    def enquiry() -> Response:
        data    = request.get_json(force=True) or {}
        name    = data.get("name", "").strip()
        phone   = data.get("phone", "").strip()
        email   = data.get("email", "").strip()
        plan    = data.get("plan", "Not selected")
        message = data.get("message", "").strip()

        if not (name and phone and email):
            return jsonify(ok=False, error="Missing required fields"), 400

        subject = f"[KolkataCloud] VPS Enquiry from {name} - Plan: {plan}"
        body = (
            f"New enquiry via KolkataCloud.in\n{'='*48}\n"
            f"Name    : {name}\n"
            f"Phone   : {phone}\n"
            f"Email   : {email}\n"
            f"Plan    : {plan}\n"
            f"{'='*48}\n"
            f"Message :\n{message}\n"
        )

        try:
            msg_obj = MIMEMultipart()
            msg_obj["From"]     = SMTP_USER
            msg_obj["To"]       = f"{SALES_EMAIL}, {ENQUIRY_EMAIL}"
            msg_obj["Subject"]  = subject
            msg_obj["Reply-To"] = email
            msg_obj.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as srv:
                srv.starttls()
                srv.login(SMTP_USER, SMTP_PASS)
                srv.sendmail(SMTP_USER, [SALES_EMAIL, ENQUIRY_EMAIL], msg_obj.as_string())

            return jsonify(ok=True)
        except Exception as ex:
            print(f"[MAIL ERROR] {ex}")
            return jsonify(ok=False, error=str(ex)), 500

    return app


# ── Expose app at module level for Gunicorn ───────────────────────────────────
# Gunicorn imports this module and looks for the `app` variable.
# This must be at module level, outside __main__.
app = create_flask_app()

# ── Entry point (local dev only) ──────────────────────────────────────────────
if __name__ == "__main__":
    if app:
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting dev server on port {port}  (Python {sys.version})")
        print(f"  Sales mail    : {SALES_EMAIL}")
        print(f"  Enquiry mail  : {ENQUIRY_EMAIL}")
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        out = "index.html"
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(render_page())
        print(f"Written to {out}  (Python {sys.version})")
        print("Install Flask (`pip install flask`) to run as a live server.")
