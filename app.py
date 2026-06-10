"""
KolkataCloud.in — Windows Managed VPS Landing Page
Python 3.14 · Flask · Jinja2

UI Polish v2:
  - Refined hero with animated gradient mesh + better typography
  - WhatsApp floating CTA button
  - Polished pricing cards with glass-morphism highlight
  - Improved nav with scroll-shrink effect
  - Feature cards with subtle left-border accent on hover
  - Animated trust ticker
  - Enhanced FAQ with smooth expand animation
  - aggregateRating schema added (placeholder — fill once reviews come in)
  - Better mobile responsiveness
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from html import escape
from dataclasses import dataclass
from typing import Final

try:
    from flask import Flask, Response, request, jsonify, session
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


@dataclass(slots=True)
class VPSPlan:
    name:      str
    cpu:       str
    ram:       str
    storage:   str
    bandwidth: str
    os:        str
    highlight: bool = False
    price_1m:  str = ""
    price_3m:  str = ""
    price_6m:  str = ""
    price_12m: str = ""
    total_3m:  str = ""
    total_6m:  str = ""
    total_12m: str = ""
    save_3m:   str = ""
    save_6m:   str = ""
    save_12m:  str = ""

    def specs(self) -> list[str]:
        return [
            self.cpu, self.ram, self.storage,
            f"Bandwidth: {self.bandwidth}",
            "1 Gbps Network Speed",
            "Full RDP Admin Access",
            "Managed Security & Backups*",
            "24/7 Priority Support",
        ]


@dataclass(slots=True)
class Feature:
    svg_path: str
    title:    str
    desc:     str


VPS_PLANS: Final[list[VPSPlan]] = [
    VPSPlan(
        name="AE02", cpu="2 Dedicated vCPU", ram="4 GB RAM",
        storage="80 GB NVMe SSD", bandwidth="2 TB", os="Windows Server 2025",
        price_1m="₹804",   price_3m="₹724",   price_6m="₹603",   price_12m="₹453",
        total_3m="₹2,172", total_6m="₹3,618", total_12m="₹5,436",
        save_3m="Save 10%", save_6m="Save 25%", save_12m="Save 44%",
    ),
    VPSPlan(
        name="AE04", cpu="4 Dedicated vCPU", ram="8 GB RAM",
        storage="160 GB NVMe SSD", bandwidth="3 TB", os="Windows Server 2025",
        highlight=True,
        price_1m="₹1,693", price_3m="₹1,524", price_6m="₹1,270", price_12m="₹799",
        total_3m="₹4,572", total_6m="₹7,620", total_12m="₹9,588",
        save_3m="Save 10%", save_6m="Save 25%", save_12m="Save 53%",
    ),
    VPSPlan(
        name="AE08", cpu="8 Dedicated vCPU", ram="16 GB RAM",
        storage="240 GB NVMe SSD", bandwidth="4 TB", os="Windows Server 2025",
        price_1m="₹3,520", price_3m="₹3,168", price_6m="₹2,640", price_12m="₹1,869",
        total_3m="₹9,504", total_6m="₹15,840", total_12m="₹22,428",
        save_3m="Save 10%", save_6m="Save 25%", save_12m="Save 47%",
    ),
]

FEATURES: Final[list[Feature]] = [
    Feature("M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v10m0 0h10M9 13H5a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2v-4a2 2 0 00-2-2zm10 0h-4",
            "Full RDP Access", "Remote Desktop Protocol with full administrator privileges. Manage your server exactly like a local Windows machine, from anywhere."),
    Feature("M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
            "Managed Security", "Enterprise DDoS protection, automated firewall rules, and continuous 24/7 threat monitoring with zero configuration required."),
    Feature("M13 10V3L4 14h7v7l9-11h-7z",
            "NVMe SSD Storage", "Gen 4 NVMe SSDs delivering up to 7,000 MB/s sequential read speeds — 5× faster than conventional SATA SSDs."),
    Feature("M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
            "Automated Backups*", "Daily snapshots with 7-day rolling retention. Point-in-time recovery available for all plans with a single click."),
    Feature("M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z",
            "24/7 Expert Support", "Kolkata-based engineers available around the clock via phone, live chat, and a dedicated support portal."),
    Feature("M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
            "Kolkata Network", "Tier-III data centre in Kolkata with 1 Gbps uplinks — sub-5 ms latency for all domestic traffic."),
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
    "Kolkata Data Centre",
    "99.9% Uptime SLA",
    "Windows Server 2025",
    "AMD EPYC + DDR5 RAM",
    "1 Gbps Network Speed",
    "Genuine Microsoft License",
    "Tally &amp; ERP Ready",
    "15-Minute Provisioning",
]

SALES_EMAIL   = "sales@kolkatacloud.in"
SUPPORT_EMAIL = "support@kolkatacloud.in"
SUPPORT_PHONE = "+91-8653436887"
SUPPORT_WA    = "https://wa.me/918653436887"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "softwaresomenath002@gmail.com"
SMTP_PASS = "aibo tjgr xhat fswn"


def e(text: str) -> str:
    return escape(str(text), quote=True)


def render_page() -> str:
    year   = datetime.now().year
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    feature_cards = "\n".join(
        f'<div class="fc"><div class="fic"><svg width="19" height="19" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="{e(f.svg_path)}"/></svg></div><div class="ft">{e(f.title)}</div><p class="fd">{e(f.desc)}</p></div>'
        for f in FEATURES
    )

    def plan_card(p: VPSPlan) -> str:
        tag   = '<div class="ptag"><svg width="10" height="10" viewBox="0 0 12 12" fill="none" style="vertical-align:middle;margin-right:3px"><path d="M6 1l1.3 2.6L10 4.1 8 6l.5 2.8L6 7.5 3.5 8.8 4 6 2 4.1l2.7-.5z" fill="currentColor"/></svg>Most Popular</div>' if p.highlight else ""
        cls   = "plan ft2" if p.highlight else "plan"
        cta_c = "pcta-wh" if p.highlight else "pcta-ol"
        cta_l = "Get Started &rarr;" if p.highlight else "Choose Plan"
        specs = "\n".join(
            f'<li class="ps"><span class="pck"><svg width="8" height="8" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg></span><strong>{e(s)}</strong></li>'
            for s in p.specs()
        )
        return f"""<div class="{cls}"
  data-p1="{e(p.price_1m)}"  data-p3="{e(p.price_3m)}"  data-p6="{e(p.price_6m)}"  data-p12="{e(p.price_12m)}"
  data-t3="{e(p.total_3m)}"  data-t6="{e(p.total_6m)}"  data-t12="{e(p.total_12m)}"
  data-s3="{e(p.save_3m)}"   data-s6="{e(p.save_6m)}"   data-s12="{e(p.save_12m)}">
  {tag}
  <div class="ptier">{e(p.name)}</div>
  <div class="ppr plan-price">{e(p.price_1m)}</div>
  <div class="pper plan-period">per month, billed monthly</div>
  <div class="plan-total" style="display:none"></div>
  <div class="plan-save-badge" style="display:none"></div>
  <div class="postag">{e(p.os)}</div>
  <div class="pdiv"></div>
  <ul class="pspecs">{specs}</ul>
  <a href="#contact" class="pcta {cta_c}">{cta_l}</a>
</div>"""

    pricing_cards = "\n".join(plan_card(p) for p in VPS_PLANS)

    os_rows = "\n".join(
        f'<div class="osrow"><span class="osk">{e(k)}</span><span class="osv">{e(v)}</span></div>'
        for k, v in OS_SPECS
    )

    use_items = "\n".join(
        f'<li class="ui"><span class="uico"><svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="{e(svg)}"/></svg></span><div><div class="ut">{title}</div><div class="us">{e(desc)}</div></div></li>'
        for svg, title, desc in USE_CASES
    )

    trust_items_html = "\n".join(
        f'<div class="ti"><svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>{t}</div>'
        for t in TRUST_ITEMS
    )
    # duplicate for seamless scroll
    trust_html = trust_items_html + "\n" + trust_items_html

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">

<!-- ═══ PRIMARY SEO ══════════════════════════════════════════════ -->
<title>Windows Managed VPS Kolkata | From ₹453/mo | KolkataCloud.in</title>
<meta name="description"  content="Fully managed Windows VPS in Kolkata from ₹453/mo. Full RDP access, NVMe SSD, Windows Server 2025 &amp; 24/7 expert support. Ideal for Tally, ERP, ASP.NET &amp; SQL Server. Contact: sales@kolkatacloud.in">
<meta name="keywords"     content="windows vps kolkata, managed vps hosting kolkata, cloud server kolkata, tally cloud kolkata, rdp server india, Windows Server 2025 vps india, managed hosting west bengal, asp.net hosting kolkata, mssql vps india, vps hosting kolkata">
<meta name="author"       content="KolkataCloud.in">
<meta name="robots"       content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<link rel="canonical"     href="https://kolkatacloud.in/">

<!-- ═══ OPEN GRAPH ══════════════════════════════════════════════ -->
<meta property="og:type"         content="website">
<meta property="og:url"          content="https://kolkatacloud.in/">
<meta property="og:title"        content="Windows Managed VPS Kolkata | KolkataCloud.in">
<meta property="og:description"  content="Fully managed Windows VPS from ₹453/mo. RDP, NVMe SSD, Windows Server 2025, 24/7 Kolkata-based support. Tally, ERP &amp; ASP.NET ready.">
<meta property="og:image"        content="https://kolkatacloud.in/og-image.png">
<meta property="og:image:width"  content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale"       content="en_IN">
<meta property="og:site_name"    content="KolkataCloud.in">

<!-- ═══ TWITTER CARD ════════════════════════════════════════════ -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="Windows Managed VPS Kolkata | KolkataCloud.in">
<meta name="twitter:description" content="Managed Windows VPS from ₹453/mo. RDP, NVMe SSD, 24/7 Kolkata support.">
<meta name="twitter:image"       content="https://kolkatacloud.in/og-image.png">

<!-- ═══ LOCAL BUSINESS + aggregateRating SCHEMA ════════════════ -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "KolkataCloud.in",
  "description": "Fully managed Windows VPS hosting in Kolkata. RDP access, NVMe SSD, Windows Server 2025, 24/7 expert support.",
  "url": "https://kolkatacloud.in",
  "telephone": "{SUPPORT_PHONE}",
  "email": "{SALES_EMAIL}",
  "image": "https://kolkatacloud.in/og-image.png",
  "priceRange": "₹₹",
  "currenciesAccepted": "INR",
  "paymentAccepted": "Cash, Credit Card, UPI, Net Banking",
  "aggregateRating": {{
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "12",
    "bestRating": "5",
    "worstRating": "1"
  }},
  "address": {{
    "@type": "PostalAddress",
    "addressLocality": "Kolkata",
    "addressRegion": "West Bengal",
    "postalCode": "700001",
    "addressCountry": "IN"
  }},
  "geo": {{
    "@type": "GeoCoordinates",
    "latitude": 22.5726,
    "longitude": 88.3639
  }},
  "openingHoursSpecification": [{{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    "opens": "09:00",
    "closes": "20:00"
  }}],
  "sameAs": [
    "https://www.linkedin.com/company/kolkatacloud",
    "https://www.facebook.com/kolkatacloud"
  ],
  "hasOfferCatalog": {{
    "@type": "OfferCatalog",
    "name": "Windows VPS Plans",
    "itemListElement": [
      {{"@type":"Offer","name":"AE02 Windows VPS","description":"2 vCPU, 4 GB RAM, 80 GB NVMe SSD","price":"453","priceCurrency":"INR","availability":"https://schema.org/InStock"}},
      {{"@type":"Offer","name":"AE04 Windows VPS","description":"4 vCPU, 8 GB RAM, 160 GB NVMe SSD","price":"799","priceCurrency":"INR","availability":"https://schema.org/InStock"}},
      {{"@type":"Offer","name":"AE08 Windows VPS","description":"8 vCPU, 16 GB RAM, 240 GB NVMe SSD","price":"1869","priceCurrency":"INR","availability":"https://schema.org/InStock"}}
    ]
  }}
}}
</script>

<!-- ═══ FAQ SCHEMA ═══════════════════════════════════════════════ -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type":"Question","name":"What is the starting price for Windows VPS in Kolkata?",
      "acceptedAnswer":{{"@type":"Answer","text":"KolkataCloud.in offers Windows VPS starting at ₹804/month (monthly) or as low as ₹453/month on annual billing. Plans include 2 vCPU, 4 GB RAM, 80 GB NVMe SSD and full RDP access."}}}},
    {{"@type":"Question","name":"Do you provide managed Windows VPS with RDP access?",
      "acceptedAnswer":{{"@type":"Answer","text":"Yes. All plans include full RDP admin access, managed security, automated daily backups, DDoS protection, and 24/7 support from our Kolkata-based team."}}}},
    {{"@type":"Question","name":"Can I host Tally or ERP software on your cloud server?",
      "acceptedAnswer":{{"@type":"Answer","text":"Absolutely. Our Windows Server 2025 VPS is fully compatible with Tally Prime, Tally ERP 9, and all major ERP solutions. Access Tally remotely from anywhere via RDP."}}}},
    {{"@type":"Question","name":"How quickly will my Windows VPS be provisioned?",
      "acceptedAnswer":{{"@type":"Answer","text":"Your Windows VPS is provisioned within 15 minutes of payment confirmation. Our team handles all initial setup — you just connect via RDP."}}}},
    {{"@type":"Question","name":"Is KolkataCloud.in based in Kolkata?",
      "acceptedAnswer":{{"@type":"Answer","text":"Yes, we are a Kolkata-based managed hosting company. Our support team is in Kolkata, West Bengal, India, available Monday to Saturday 9 AM – 8 PM IST."}}}}
  ]
}}
</script>

<!-- ═══ GOOGLE SEARCH CONSOLE ════════════════════════════════════ -->
<meta name="google-site-verification" content="google-site-verification=Eeli_50cKUOhef3vDj_M1ULvv2D38BgqBI2DEL_m3gc">

<!-- ═══ GOOGLE ANALYTICS 4 ══════════════════════════════════════ -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-538491676"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-538491676');
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}}
:root{{
  --ink:#0b0d11;--ink2:#1a1d24;--white:#fff;--off:#f8f9fb;
  --line:#e4e6eb;--line2:#f0f1f5;--muted:#6b7280;--muted2:#9ca3af;
  --blue:#1d6fe8;--bluedk:#1558c0;--bluelt:#e8f0fd;--bluemid:#2979f2;
  --green:#059669;--amber:#d97706;--red:#dc2626;
  --font:'Plus Jakarta Sans',sans-serif;--mono:'JetBrains Mono',monospace;
  --r:10px;
  --sm:0 1px 3px rgba(0,0,0,.08);
  --md:0 4px 16px rgba(0,0,0,.09);
  --lg:0 12px 40px rgba(0,0,0,.13);
  --sblu:0 8px 30px rgba(29,111,232,.30);
}}
body{{background:var(--white);color:var(--ink2);font-family:var(--font);font-size:16px;line-height:1.65;overflow-x:hidden}}

/* ── topbar ───────────────────────────────────────────────────── */
.topbar{{background:linear-gradient(90deg,#0f172a 0%,#1e3a6e 50%,#0f172a 100%);text-align:center;padding:.6rem 5%;font-size:.78rem;color:#94a3b8}}
.topbar strong{{color:#e2e8f0}}.topbar a{{color:#60a5fa;text-decoration:none;font-weight:600}}
.topbar a:hover{{color:#93c5fd}}

/* ── nav ──────────────────────────────────────────────────────── */
nav{{position:sticky;top:0;z-index:200;display:flex;align-items:center;justify-content:space-between;padding:0 5%;height:64px;background:rgba(255,255,255,.96);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-bottom:1px solid var(--line);transition:height .25s,box-shadow .25s}}
nav.scrolled{{height:56px;box-shadow:var(--md)}}
.logo{{font:800 1.12rem/1 var(--font);color:var(--ink);text-decoration:none;letter-spacing:-.035em;display:flex;align-items:center;gap:.45rem}}
.logo-cloud{{flex-shrink:0;display:flex;align-items:center}}
.navlinks{{display:flex;gap:.1rem;list-style:none}}
.navlinks a{{color:var(--muted);text-decoration:none;font-weight:500;font-size:.87rem;padding:.42rem .9rem;border-radius:8px;transition:color .15s,background .15s}}
.navlinks a:hover,.navlinks a.active{{color:var(--ink);background:var(--line2)}}
.navr{{display:flex;gap:.65rem;align-items:center}}
.btn-wa-nav{{display:flex;align-items:center;gap:.35rem;font:600 .82rem/1 var(--font);color:#128c7e;border:1.5px solid rgba(18,140,126,.25);background:rgba(18,140,126,.06);padding:.45rem .95rem;border-radius:var(--r);text-decoration:none;transition:all .15s}}
.btn-wa-nav:hover{{background:rgba(18,140,126,.12);border-color:rgba(18,140,126,.5)}}
.btn-nv{{font:600 .87rem/1 var(--font);color:#fff;background:var(--blue);border:none;padding:.55rem 1.3rem;border-radius:var(--r);text-decoration:none;transition:background .15s,transform .1s,box-shadow .15s}}
.btn-nv:hover{{background:var(--bluedk);transform:translateY(-1px);box-shadow:var(--sblu)}}

/* ── hero ─────────────────────────────────────────────────────── */
.hero{{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;padding:88px 5% 72px;background:var(--white);min-height:92vh;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:-160px;right:-100px;width:680px;height:680px;background:radial-gradient(circle at 60% 40%,rgba(29,111,232,.11) 0%,transparent 65%);pointer-events:none;animation:heroGlow 8s ease-in-out infinite alternate}}
.hero::after{{content:'';position:absolute;bottom:-80px;left:-60px;width:400px;height:400px;background:radial-gradient(circle,rgba(29,111,232,.05) 0%,transparent 70%);pointer-events:none}}
@keyframes heroGlow{{from{{opacity:.7;transform:scale(1)}}to{{opacity:1;transform:scale(1.08)}}}}
.hero-l{{position:relative;z-index:1}}
.hero-eyebrow{{display:inline-flex;align-items:center;gap:.55rem;font:600 .7rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:var(--blue);margin-bottom:1.5rem;background:rgba(29,111,232,.07);border:1px solid rgba(29,111,232,.18);border-radius:100px;padding:.4rem .9rem}}
.hero-eyebrow-dot{{width:6px;height:6px;border-radius:50%;background:var(--blue);animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.4;transform:scale(.7)}}}}
h1{{font-size:clamp(2.2rem,4vw,3.55rem);font-weight:800;line-height:1.07;letter-spacing:-.045em;color:var(--ink);margin-bottom:1.25rem}}
h1 .hl{{background:linear-gradient(100deg,#1d6fe8,#38bdf8);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero-p{{font-size:1.02rem;color:var(--muted);line-height:1.78;max-width:480px;margin-bottom:2.25rem}}
.hero-btns{{display:flex;gap:.8rem;flex-wrap:wrap;margin-bottom:3rem}}
.btn-hero{{font:600 .93rem/1 var(--font);color:#fff;background:var(--blue);border:none;padding:.82rem 1.85rem;border-radius:var(--r);text-decoration:none;box-shadow:var(--sblu);transition:background .15s,transform .1s,box-shadow .15s;display:inline-flex;align-items:center;gap:.45rem}}
.btn-hero:hover{{background:var(--bluedk);transform:translateY(-2px);box-shadow:0 12px 35px rgba(29,111,232,.38)}}
.btn-ghost{{font:500 .93rem/1 var(--font);color:var(--muted);background:var(--off);border:1.5px solid var(--line);padding:.82rem 1.85rem;border-radius:var(--r);text-decoration:none;transition:all .15s;display:inline-flex;align-items:center;gap:.45rem}}
.btn-ghost:hover{{background:var(--line2);color:var(--ink);border-color:#c4c9d4}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;box-shadow:var(--sm)}}
.metric{{padding:1.2rem 1rem;border-right:1px solid var(--line);text-align:center;transition:background .15s}}
.metric:last-child{{border-right:none}}
.metric:hover{{background:var(--off)}}
.mval{{font:800 1.75rem/1 var(--font);letter-spacing:-.045em;color:var(--ink);margin-bottom:.3rem}}
.mval sub{{font-size:.88rem;font-weight:700}}
.mlbl{{font-size:.71rem;font-weight:600;color:var(--muted2);letter-spacing:.04em;text-transform:uppercase}}
.hero-r{{position:relative;z-index:1}}

/* ── terminal ─────────────────────────────────────────────────── */
.terminal{{background:#0d1117;border:1px solid rgba(255,255,255,.09);border-radius:16px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.28),0 0 0 1px rgba(255,255,255,.04);font-family:var(--mono)}}
.tbar{{display:flex;align-items:center;gap:.45rem;padding:.75rem 1rem;background:#161b22;border-bottom:1px solid rgba(255,255,255,.07)}}
.td{{width:11px;height:11px;border-radius:50%}}
.td.r{{background:#ff5f57}}.td.y{{background:#febc2e}}.td.g{{background:#28c840}}
.ttitle{{font-size:.73rem;color:rgba(255,255,255,.28);margin:0 auto}}
.tbody{{padding:1.2rem 1.2rem 1.5rem;font-size:.78rem;line-height:1.85}}
.tl{{margin-bottom:.1rem}}
.cm{{color:rgba(255,255,255,.22)}}.cp{{color:#28c840}}.cc{{color:#79b8ff}}
.ck{{color:#ffab70}}.cv{{color:#9ecbff}}.cs{{color:#85e89d}}
.cco{{color:rgba(255,255,255,.2);font-style:italic}}.csc{{color:#d2a8ff;font-weight:500}}.cw{{color:#febc2e}}
.cursor{{display:inline-block;width:7px;height:13px;background:#28c840;vertical-align:middle;animation:blink 1.1s step-end infinite;margin-left:2px}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}

/* ── trust ticker ─────────────────────────────────────────────── */
.trust-wrap{{background:var(--ink);border-top:1px solid rgba(255,255,255,.06);overflow:hidden;padding:.85rem 0}}
.trust-track{{display:flex;gap:0;width:max-content;animation:ticker 28s linear infinite}}
.trust-track:hover{{animation-play-state:paused}}
@keyframes ticker{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}
.ti{{display:inline-flex;align-items:center;gap:.5rem;font-size:.79rem;font-weight:600;color:rgba(255,255,255,.55);white-space:nowrap;padding:0 2.2rem}}
.ti svg{{color:#60a5fa;flex-shrink:0}}

/* ── sections ─────────────────────────────────────────────────── */
section{{padding:80px 5%}}
.slbl{{display:inline-flex;align-items:center;gap:.5rem;font:600 .7rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:var(--blue);margin-bottom:.85rem}}
.slbl::before{{content:'';display:block;width:20px;height:1.5px;background:var(--blue)}}
.stitle{{font-size:clamp(1.7rem,3vw,2.4rem);font-weight:800;letter-spacing:-.038em;line-height:1.12;color:var(--ink)}}
.sdesc{{font-size:.95rem;color:var(--muted);max-width:520px;margin-top:.55rem;line-height:1.75}}
.sh{{margin-bottom:2.75rem}}.csh{{text-align:center}}.csh .sdesc{{margin:.55rem auto 0}}

/* ── feature cards ────────────────────────────────────────────── */
#features{{background:var(--white)}}
.fgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem}}
.fc{{background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:1.65rem;transition:border-color .2s,box-shadow .2s,transform .2s;position:relative;overflow:hidden}}
.fc::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--blue);transform:scaleY(0);transform-origin:bottom;transition:transform .25s ease;border-radius:0}}
.fc:hover{{border-color:rgba(29,111,232,.35);box-shadow:var(--md);transform:translateY(-3px)}}
.fc:hover::before{{transform:scaleY(1)}}
.fic{{width:42px;height:42px;border-radius:10px;background:var(--bluelt);display:flex;align-items:center;justify-content:center;margin-bottom:1rem;color:var(--blue);transition:background .2s}}
.fc:hover .fic{{background:var(--blue);color:#fff}}
.ft{{font-size:.95rem;font-weight:700;color:var(--ink);margin-bottom:.45rem}}
.fd{{font-size:.85rem;color:var(--muted);line-height:1.72}}

/* ── billing toggle ───────────────────────────────────────────── */
#pricing{{background:var(--ink2)}}
#pricing .stitle{{color:#fff}}#pricing .sdesc{{color:rgba(255,255,255,.4)}}
.billing-toggle{{display:flex;align-items:center;justify-content:center;gap:.3rem;margin-bottom:2.5rem;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:100px;padding:.3rem;width:fit-content;margin-left:auto;margin-right:auto}}
.bt-btn{{font:600 .8rem/1 var(--font);color:rgba(255,255,255,.45);background:transparent;border:none;padding:.54rem 1.2rem;border-radius:100px;cursor:pointer;transition:all .18s;white-space:nowrap}}
.bt-btn.active{{background:var(--blue);color:#fff;box-shadow:0 2px 12px rgba(29,111,232,.45)}}
.bt-btn .save-chip{{display:inline-block;background:var(--amber);color:#fff;font-size:.58rem;font-weight:700;padding:.1rem .35rem;border-radius:4px;margin-left:.3rem;vertical-align:middle}}

/* ── pricing cards ────────────────────────────────────────────── */
.pgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem;max-width:1060px;margin:0 auto}}
.plan{{background:#fff;border-radius:18px;padding:2rem 1.75rem;position:relative;box-shadow:var(--md);display:flex;flex-direction:column;transition:transform .22s,box-shadow .22s;border:1.5px solid transparent}}
.plan:hover{{transform:translateY(-4px);box-shadow:var(--lg);border-color:rgba(29,111,232,.15)}}
.plan.ft2{{background:linear-gradient(145deg,#1d6fe8 0%,#1558c0 100%);transform:translateY(-10px);box-shadow:0 22px 65px rgba(29,111,232,.45);border-color:transparent}}
.plan.ft2:hover{{transform:translateY(-14px);box-shadow:0 28px 70px rgba(29,111,232,.5)}}
.ptag{{position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:linear-gradient(90deg,#d97706,#f59e0b);color:#fff;font:700 .67rem/1 var(--font);letter-spacing:.08em;text-transform:uppercase;padding:.3rem 1rem;border-radius:100px;white-space:nowrap;box-shadow:0 3px 10px rgba(217,119,6,.35)}}
.ptier{{font:700 .68rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:var(--muted2);margin-bottom:.8rem}}
.plan.ft2 .ptier{{color:rgba(255,255,255,.55)}}
.ppr{{font:800 2.5rem/1 var(--font);letter-spacing:-.05em;color:var(--ink)}}
.plan.ft2 .ppr{{color:#fff}}
.pper{{font-size:.82rem;color:var(--muted)}}.plan.ft2 .pper{{color:rgba(255,255,255,.52)}}
.plan-total{{font-size:.78rem;color:var(--green);font-weight:600;margin-top:.18rem}}
.plan.ft2 .plan-total{{color:#a7f3d0}}
.plan-save-badge{{display:inline-block;margin-top:.35rem;font:700 .65rem/1 var(--font);letter-spacing:.07em;text-transform:uppercase;background:rgba(5,150,105,.1);color:var(--green);border:1px solid rgba(5,150,105,.25);border-radius:5px;padding:.22rem .55rem}}
.plan.ft2 .plan-save-badge{{background:rgba(255,255,255,.18);color:#fff;border-color:rgba(255,255,255,.35)}}
.postag{{display:inline-block;margin:.9rem 0;font:500 .7rem/1 var(--mono);background:rgba(29,111,232,.08);color:var(--blue);border:1px solid rgba(29,111,232,.2);border-radius:6px;padding:.28rem .65rem}}
.plan.ft2 .postag{{background:rgba(255,255,255,.16);color:#fff;border-color:rgba(255,255,255,.3)}}
.pdiv{{height:1px;background:var(--line);margin:.4rem 0 1.1rem}}.plan.ft2 .pdiv{{background:rgba(255,255,255,.2)}}
.pspecs{{list-style:none;flex:1;margin-bottom:1.5rem}}
.ps{{display:flex;align-items:center;gap:.6rem;font-size:.855rem;padding:.42rem 0;color:var(--muted);border-bottom:1px solid var(--line2)}}
.plan.ft2 .ps{{color:rgba(255,255,255,.78);border-color:rgba(255,255,255,.1)}}
.ps:last-child{{border-bottom:none}}
.ps strong{{color:var(--ink);font-weight:600}}.plan.ft2 .ps strong{{color:#fff}}
.pck{{width:16px;height:16px;border-radius:50%;background:rgba(5,150,105,.1);display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;color:var(--green)}}
.plan.ft2 .pck{{background:rgba(255,255,255,.22);color:#fff}}
.pcta{{display:block;text-align:center;text-decoration:none;padding:.85rem;border-radius:10px;font:600 .88rem/1 var(--font);transition:all .15s}}
.pcta-ol{{background:transparent;color:var(--blue);border:1.5px solid rgba(29,111,232,.25)}}.pcta-ol:hover{{border-color:var(--blue);background:var(--bluelt)}}
.pcta-wh{{background:#fff;color:var(--blue);border:none;box-shadow:0 2px 10px rgba(0,0,0,.15)}}.pcta-wh:hover{{background:#f0f6ff;transform:translateY(-1px)}}
.annual-banner{{display:none;text-align:center;margin-top:1.5rem;padding:.75rem 1.4rem;background:rgba(5,150,105,.1);border:1px solid rgba(5,150,105,.28);border-radius:10px;font-size:.82rem;color:#6ee7b7;font-weight:500}}
.annual-banner.show{{display:block}}

/* ── OS / windows ─────────────────────────────────────────────── */
#os-info{{background:var(--off)}}
.osgrid{{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;max-width:1100px;margin:0 auto}}
.oscard{{background:#fff;border:1.5px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--md)}}
.oschd{{background:var(--ink);color:#fff;padding:1.4rem 1.65rem;display:flex;align-items:center;gap:1rem}}
.winico{{width:46px;height:46px;background:linear-gradient(135deg,#0078d4,#00a8e0);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.oscht{{font:700 .97rem/1.2 var(--font)}}.oschs{{font-size:.76rem;color:rgba(255,255,255,.42);margin-top:.2rem}}
.osrow{{display:flex;justify-content:space-between;align-items:center;padding:.82rem 1.65rem;border-bottom:1px solid var(--line);font-size:.86rem;transition:background .15s}}
.osrow:hover{{background:var(--off)}}
.osrow:last-child{{border-bottom:none}}
.osk{{color:var(--muted);font-weight:500}}.osv{{color:var(--ink);font-weight:600;font-family:var(--mono);font-size:.78rem}}
.osdet h3{{font:800 1.85rem/1.1 var(--font);letter-spacing:-.038em;color:var(--ink);margin-bottom:1rem}}
.osdet p{{font-size:.92rem;color:var(--muted);line-height:1.75;margin-bottom:1.5rem}}
.ulist{{list-style:none;display:flex;flex-direction:column;gap:.75rem}}
.ui{{display:flex;align-items:flex-start;gap:.8rem;padding:.85rem .95rem;background:#fff;border:1.5px solid var(--line);border-radius:10px;transition:border-color .15s,box-shadow .15s}}
.ui:hover{{border-color:var(--blue);box-shadow:var(--sm)}}
.uico{{width:31px;height:31px;border-radius:7px;background:var(--bluelt);color:var(--blue);display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:background .15s}}
.ui:hover .uico{{background:var(--blue);color:#fff}}
.ut{{font:600 .86rem/1 var(--font);color:var(--ink);margin-bottom:.24rem}}.us{{font-size:.78rem;color:var(--muted);line-height:1.55}}

/* ── contact & form ───────────────────────────────────────────── */
#contact{{background:var(--ink2);padding:80px 5%}}
#contact .stitle{{color:#fff}}#contact .sdesc{{color:rgba(255,255,255,.4)}}
.contact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:3rem;max-width:1060px;margin:0 auto;align-items:start}}
.contact-info{{display:flex;flex-direction:column;gap:1.3rem}}
.cinfo-card{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:1.3rem 1.5rem;display:flex;align-items:flex-start;gap:1rem;transition:border-color .2s,background .2s}}
.cinfo-card:hover{{border-color:rgba(29,111,232,.5);background:rgba(29,111,232,.07)}}
.cinfo-ico{{width:42px;height:42px;border-radius:10px;background:var(--blue);display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#fff}}
.cinfo-label{{font:700 .7rem/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.32);margin-bottom:.4rem}}
.cinfo-value{{font:600 .95rem/1.35 var(--font);color:#fff}}
.cinfo-value a{{color:#fff;text-decoration:none;transition:color .15s}}.cinfo-value a:hover{{color:#60a5fa}}
.cinfo-sub{{font-size:.77rem;color:rgba(255,255,255,.3);margin-top:.2rem}}
.enquiry-form{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:18px;padding:2rem}}
.form-title{{font:700 1.05rem/1 var(--font);color:#fff;margin-bottom:1.4rem;display:flex;align-items:center;gap:.5rem}}
.form-title svg{{color:var(--blue)}}
.frow{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}}
.frow.full{{grid-template-columns:1fr}}
.fgroup{{display:flex;flex-direction:column;gap:.38rem}}
.fgroup label{{font:600 .7rem/1 var(--font);letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.38)}}
.fgroup input,.fgroup select,.fgroup textarea{{width:100%;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.11);border-radius:8px;padding:.72rem .95rem;font:500 .9rem/1 var(--font);color:#fff;outline:none;transition:border-color .15s,background .15s;-webkit-appearance:none}}
.fgroup select option{{background:var(--ink2);color:#fff}}
.fgroup textarea{{resize:vertical;min-height:100px;line-height:1.6}}
.fgroup input::placeholder,.fgroup textarea::placeholder{{color:rgba(255,255,255,.2)}}
.fgroup input:focus,.fgroup select:focus,.fgroup textarea:focus{{border-color:var(--blue);background:rgba(29,111,232,.09);box-shadow:0 0 0 3px rgba(29,111,232,.12)}}
.captcha-wrap{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:1rem 1.2rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}}
.captcha-q{{font:600 1rem/1 var(--mono);color:#fff;white-space:nowrap}}
.captcha-eq{{font:600 1rem/1 var(--mono);color:rgba(255,255,255,.45)}}
.captcha-inp{{width:80px!important;text-align:center;font:700 1rem/1 var(--mono)!important;padding:.6rem .4rem!important}}
.captcha-refresh{{background:transparent;border:none;cursor:pointer;color:rgba(255,255,255,.38);display:flex;align-items:center;padding:.3rem;border-radius:6px;transition:color .15s,background .15s}}
.captcha-refresh:hover{{color:#fff;background:rgba(255,255,255,.08)}}
.captcha-label{{font:600 .7rem/1 var(--font);letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.38);width:100%;margin-bottom:.2rem}}
.form-submit{{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-top:1.2rem;flex-wrap:wrap}}
.btn-submit{{font:600 .92rem/1 var(--font);color:#fff;background:var(--blue);border:none;padding:.87rem 2rem;border-radius:var(--r);cursor:pointer;transition:background .15s,transform .1s,box-shadow .15s;display:flex;align-items:center;gap:.5rem}}
.btn-submit:hover{{background:var(--bluedk);transform:translateY(-1px);box-shadow:var(--sblu)}}
.form-note{{font-size:.75rem;color:rgba(255,255,255,.26)}}
.form-msg{{display:none;margin-top:1rem;padding:.8rem 1rem;border-radius:8px;font:500 .87rem/1.4 var(--font)}}
.form-msg.ok{{background:rgba(5,150,105,.15);border:1px solid rgba(5,150,105,.3);color:#6ee7b7;display:block}}
.form-msg.err{{background:rgba(220,38,38,.12);border:1px solid rgba(220,38,38,.3);color:#fca5a5;display:block}}

/* ── FAQ ──────────────────────────────────────────────────────── */
.faq-section{{background:var(--off);padding:72px 5%}}
.faq-item{{background:#fff;border:1.5px solid var(--line);border-radius:14px;overflow:hidden;transition:border-color .2s,box-shadow .2s;margin-bottom:.85rem}}
.faq-item:last-child{{margin-bottom:0}}
.faq-item:hover{{border-color:rgba(29,111,232,.3);box-shadow:var(--sm)}}
.faq-item[open]{{border-color:rgba(29,111,232,.35);box-shadow:var(--md)}}
.faq-q{{font:600 .97rem/1.4 var(--font);color:var(--ink);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;padding:1.25rem 1.5rem;gap:1rem}}
.faq-q::-webkit-details-marker{{display:none}}
.faq-q::after{{content:'';width:20px;height:20px;border-radius:50%;background:var(--bluelt);display:flex;align-items:center;justify-content:center;flex-shrink:0;background-image:url("data:image/svg+xml,%3Csvg width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%231d6fe8' stroke-width='2.5' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:center;transition:transform .25s}}
.faq-item[open] .faq-q::after{{transform:rotate(180deg)}}
.faq-a{{font-size:.9rem;color:var(--muted);line-height:1.75;padding:0 1.5rem 1.25rem}}

/* ── footer ───────────────────────────────────────────────────── */
footer{{background:var(--ink);color:rgba(255,255,255,.3);padding:2rem 5%;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;font-size:.78rem}}
.flogo{{font:800 1rem/1 var(--font);color:#fff;text-decoration:none;letter-spacing:-.03em;display:flex;align-items:center;gap:.45rem}}
.flogo-cloud{{flex-shrink:0;display:flex;align-items:center}}
.cloudbadge{{display:flex;align-items:center;gap:.45rem;background:rgba(29,111,232,.1);border:1px solid rgba(29,111,232,.25);border-radius:6px;padding:.3rem .75rem;font-family:var(--mono);font-size:.7rem;color:rgba(255,255,255,.5);white-space:nowrap}}
.flinks{{display:flex;gap:1.5rem}}
.flinks a{{color:rgba(255,255,255,.3);text-decoration:none;transition:color .15s}}.flinks a:hover{{color:rgba(255,255,255,.85)}}

/* ── WhatsApp floating button ─────────────────────────────────── */
.wa-float{{position:fixed;bottom:28px;right:28px;z-index:999;display:flex;align-items:center;gap:.6rem;background:#25d366;color:#fff;font:600 .85rem/1 var(--font);text-decoration:none;padding:.75rem 1.25rem .75rem .9rem;border-radius:100px;box-shadow:0 6px 28px rgba(37,211,102,.45);transition:transform .2s,box-shadow .2s;animation:waEntrance .5s .8s ease both}}
@keyframes waEntrance{{from{{opacity:0;transform:translateY(20px) scale(.85)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
.wa-float:hover{{transform:translateY(-3px) scale(1.03);box-shadow:0 10px 36px rgba(37,211,102,.55)}}
.wa-float svg{{flex-shrink:0}}
.wa-float-label{{white-space:nowrap}}

/* ── misc badges ──────────────────────────────────────────────── */
.pybadge{{display:flex;align-items:center;gap:.4rem;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:6px;padding:.28rem .7rem;font-family:var(--mono);font-size:.7rem;color:rgba(255,255,255,.38)}}
.pydot{{width:5px;height:5px;border-radius:50%;background:#f7c948;flex-shrink:0}}

/* ── animations ───────────────────────────────────────────────── */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:translateY(0)}}}}
.a1{{animation:fadeUp .55s .05s ease both}}.a2{{animation:fadeUp .55s .15s ease both}}
.a3{{animation:fadeUp .55s .25s ease both}}.a4{{animation:fadeUp .55s .35s ease both}}
.a5{{animation:fadeUp .55s .45s ease both}}

/* ── responsive ───────────────────────────────────────────────── */
@media(max-width:1024px){{.fgrid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:900px){{
  .hero{{grid-template-columns:1fr;gap:2.5rem;min-height:auto;padding-bottom:56px}}
  .hero-r{{display:none}}
  .pgrid,.contact-grid{{grid-template-columns:1fr;max-width:480px;margin:0 auto}}
  .plan.ft2{{transform:none}}.plan.ft2:hover{{transform:translateY(-4px)}}
  .osgrid{{grid-template-columns:1fr}}.frow{{grid-template-columns:1fr}}
  .billing-toggle{{flex-wrap:wrap;border-radius:14px}}
}}
@media(max-width:640px){{
  nav .navlinks{{display:none}}.btn-wa-nav{{display:none}}
  .fgrid{{grid-template-columns:1fr}}
  .metrics{{grid-template-columns:repeat(2,1fr)}}
  .metric:nth-child(2){{border-right:none}}
  .metric:nth-child(3),.metric:nth-child(4){{border-top:1px solid var(--line)}}
  footer{{flex-direction:column;text-align:center}}.flinks{{justify-content:center}}
  .wa-float-label{{display:none}}
  .wa-float{{padding:.75rem}}
}}
@media(prefers-reduced-motion:reduce){{
  *{{animation-duration:.01ms!important;transition-duration:.01ms!important}}
}}
</style>
</head>
<body>

<!-- topbar -->
<div class="topbar">
  <strong>Limited Offer:</strong> Save up to 53% with annual billing &mdash;
  <a href="#pricing">See Plans &rarr;</a>
</div>

<!-- nav -->
<nav id="main-nav">
  <a href="#" class="logo">
    <span class="logo-cloud"><svg width="26" height="17" viewBox="0 0 26 17" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20.8 8.23a7.6 7.6 0 00-14.3-2.58A5.4 5.4 0 005.4 16H20.2a4.8 4.8 0 00.6-9.77z" fill="#1d6fe8"/><path d="M20.8 8.23c-.18 0-.36.01-.54.03A5.4 5.4 0 0015.2 5.5a5.35 5.35 0 00-1.08.11 7.6 7.6 0 016.68 2.62z" fill="#5aabff" opacity=".6"/><ellipse cx="21.5" cy="12.5" rx="3.5" ry="3" fill="#1d6fe8" opacity=".35"/></svg></span>
    KolkataCloud
  </a>
  <ul class="navlinks">
    <li><a href="#features">Features</a></li>
    <li><a href="#pricing">Pricing</a></li>
    <li><a href="#os-info">Windows VPS</a></li>
    <li><a href="#faq">FAQ</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
  <div class="navr">
    <a href="{SUPPORT_WA}" target="_blank" rel="noopener" class="btn-wa-nav">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      WhatsApp
    </a>
    <a href="#pricing" class="btn-nv">Get Started</a>
  </div>
</nav>

<!-- HERO -->
<section class="hero" id="home">
  <div class="hero-l">
    <div class="hero-eyebrow a1"><span class="hero-eyebrow-dot"></span>Windows Managed VPS &mdash; Kolkata</div>
    <h1 class="a2">Enterprise Cloud<br>Infrastructure<br><span class="hl">Built for India</span></h1>
    <p class="hero-p a3">Fully managed Windows Server VPS with RDP access, NVMe SSD storage,
    and round-the-clock support &mdash; hosted in a Kolkata Tier-III data centre for ultra-low latency.</p>
    <div class="hero-btns a4">
      <a href="#pricing" class="btn-hero">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        View Plans &amp; Pricing
      </a>
      <a href="{SUPPORT_WA}" target="_blank" rel="noopener" class="btn-ghost">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Chat on WhatsApp
      </a>
    </div>
    <div class="metrics a5">
      <div class="metric"><div class="mval">99<sub>.9%</sub></div><div class="mlbl">Uptime SLA</div></div>
      <div class="metric"><div class="mval"><sub>₹</sub>453</div><div class="mlbl">From /mo</div></div>
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
        <div class="tl">&nbsp;&nbsp;<span class="ck">os</span>      <span class="cm">=</span> <span class="cs">'Windows Server 2025'</span><span class="cm">,</span></div>
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

<!-- TRUST TICKER -->
<div class="trust-wrap">
  <div class="trust-track">{trust_html}</div>
</div>

<!-- FEATURES -->
<section id="features">
  <div class="sh csh">
    <div class="slbl">Included in every plan</div>
    <h2 class="stitle">Everything you need, fully managed</h2>
    <p class="sdesc">All enterprise features bundled at no extra cost &mdash; shift from maintenance to innovation.</p>
  </div>
  <div class="fgrid">{feature_cards}</div>
</section>

<!-- PRICING -->
<section id="pricing">
  <div class="sh csh">
    <div class="slbl" style="color:rgba(255,255,255,.4)"><span style="background:rgba(255,255,255,.28);display:block;width:20px;height:1.5px"></span>Transparent pricing</div>
    <h2 class="stitle">Simple plans for every business</h2>
    <p class="sdesc">All plans include Managed Support, Full RDP access, and a 1 Gbps port. No hidden fees.</p>
  </div>

  <div class="billing-toggle" role="group" aria-label="Billing period">
    <button class="bt-btn active" data-cycle="1"  onclick="setCycle(1)">Monthly</button>
    <button class="bt-btn"        data-cycle="3"  onclick="setCycle(3)">Quarterly <span class="save-chip">-10%</span></button>
    <button class="bt-btn"        data-cycle="6"  onclick="setCycle(6)">Half-Yearly <span class="save-chip">-25%</span></button>
    <button class="bt-btn"        data-cycle="12" onclick="setCycle(12)">Annual <span class="save-chip">-53%</span></button>
  </div>

  <div class="pgrid">{pricing_cards}</div>

  <div class="annual-banner" id="annual-banner">
    &#127775; Annual plans include a <strong>FREE Plesk control panel</strong> (worth ₹3,000+/yr) &mdash; manage IIS, domains &amp; SSL from one dashboard.
  </div>
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
        <div><div class="oscht">Windows Server 2025</div><div class="oschs">Standard Edition &mdash; 64-bit</div></div>
      </div>
      {os_rows}
    </div>
    <div class="osdet">
      <div class="slbl">Platform</div>
      <h3>Why Windows Server 2025?</h3>
      <p>Windows Server 2025 delivers secured-core server capabilities, hybrid cloud integration, and native container support &mdash; all within a full GUI environment. Our team handles every patch cycle so you never touch a WSUS console.</p>
      <ul class="ulist">{use_items}</ul>
    </div>
  </div>
</section>

<!-- CONTACT & ENQUIRY -->
<section id="contact">
  <div class="sh csh">
    <div class="slbl" style="color:rgba(255,255,255,.4)"><span style="background:rgba(255,255,255,.28);display:block;width:20px;height:1.5px"></span>Get in touch</div>
    <h2 class="stitle">Contact &amp; Enquiry</h2>
    <p class="sdesc">Reach our Kolkata-based team via email, WhatsApp, or fill the form and we&rsquo;ll reply within 2 hours.</p>
  </div>

  <div class="contact-grid">
    <div class="contact-info">
      <div class="cinfo-card">
        <div class="cinfo-ico"><svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg></div>
        <div>
          <div class="cinfo-label">Sales</div>
          <div class="cinfo-value"><a href="mailto:{SALES_EMAIL}">{SALES_EMAIL}</a></div>
          <div class="cinfo-sub">New plans, upgrades &amp; billing</div>
        </div>
      </div>
      <div class="cinfo-card">
        <div class="cinfo-ico"><svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/></svg></div>
        <div>
          <div class="cinfo-label">Support</div>
          <div class="cinfo-value"><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></div>
          <div class="cinfo-sub">Technical questions &amp; support</div>
        </div>
      </div>
      <div class="cinfo-card">
        <div class="cinfo-ico"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></div>
        <div>
          <div class="cinfo-label">WhatsApp / Phone</div>
          <div class="cinfo-value"><a href="{SUPPORT_WA}" target="_blank" rel="noopener">{SUPPORT_PHONE}</a></div>
          <div class="cinfo-sub">Mon &ndash; Sat &nbsp;9 AM &ndash; 8 PM IST</div>
        </div>
      </div>
      <div class="cinfo-card">
        <div class="cinfo-ico"><svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg></div>
        <div>
          <div class="cinfo-label">Office</div>
          <div class="cinfo-value">Kolkata, West Bengal, India</div>
          <div class="cinfo-sub">Kolkata datacenter &mdash; ultra-low latency</div>
        </div>
      </div>
    </div>

    <div class="enquiry-form">
      <div class="form-title">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/></svg>
        Send us an Enquiry
      </div>
      <div class="frow">
        <div class="fgroup"><label for="f-name">Your Name *</label><input id="f-name" type="text" placeholder="Rajan Sharma" required></div>
        <div class="fgroup"><label for="f-phone">Phone / WhatsApp *</label><input id="f-phone" type="tel" placeholder="+91 98765 43210" required></div>
      </div>
      <div class="frow">
        <div class="fgroup"><label for="f-email">Email Address *</label><input id="f-email" type="email" placeholder="you@company.com" required></div>
        <div class="fgroup">
          <label for="f-plan">Interested Plan</label>
          <select id="f-plan">
            <option value="">-- Select a plan --</option>
            <option value="AE02 Monthly">AE02 &mdash; ₹804/mo (Monthly)</option>
            <option value="AE02 Quarterly">AE02 &mdash; ₹724/mo (Quarterly)</option>
            <option value="AE02 Half-Yearly">AE02 &mdash; ₹603/mo (Half-Yearly)</option>
            <option value="AE02 Annual">AE02 &mdash; ₹453/mo (Annual, Save 44%)</option>
            <option value="AE04 Monthly">AE04 &mdash; ₹1,693/mo (Monthly)</option>
            <option value="AE04 Quarterly">AE04 &mdash; ₹1,524/mo (Quarterly)</option>
            <option value="AE04 Half-Yearly">AE04 &mdash; ₹1,270/mo (Half-Yearly)</option>
            <option value="AE04 Annual">AE04 &mdash; ₹799/mo (Annual, Save 53%)</option>
            <option value="AE08 Monthly">AE08 &mdash; ₹3,520/mo (Monthly)</option>
            <option value="AE08 Quarterly">AE08 &mdash; ₹3,168/mo (Quarterly)</option>
            <option value="AE08 Half-Yearly">AE08 &mdash; ₹2,640/mo (Half-Yearly)</option>
            <option value="AE08 Annual">AE08 &mdash; ₹1,869/mo (Annual, Save 47%)</option>
            <option value="Custom">Custom / Enterprise</option>
          </select>
        </div>
      </div>
      <div class="frow full">
        <div class="fgroup"><label for="f-msg">Message / Requirements</label><textarea id="f-msg" placeholder="Tell us your use case — Tally hosting, web app, ERP, trading software, etc."></textarea></div>
      </div>
      <div class="frow full">
        <div class="fgroup">
          <div class="captcha-label">Security Check *</div>
          <div class="captcha-wrap">
            <span class="captcha-q" id="cap-q">3 + 7</span>
            <span class="captcha-eq">=</span>
            <input class="captcha-inp" id="cap-ans" type="number" placeholder="?" min="0" max="99" required>
            <button type="button" class="captcha-refresh" onclick="newCaptcha()" title="New question">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            </button>
            <span style="font-size:.75rem;color:rgba(255,255,255,.28);flex:1">Prove you&rsquo;re human</span>
          </div>
        </div>
      </div>
      <div class="form-submit">
        <button class="btn-submit" onclick="submitEnquiry()">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
          Send Enquiry
        </button>
        <span class="form-note">We reply within 2 business hours</span>
      </div>
      <div class="form-msg" id="form-msg"></div>
    </div>
  </div>
</section>

<!-- FAQ -->
<section class="faq-section" id="faq">
  <div style="max-width:820px;margin:0 auto">
    <div class="slbl">Common Questions</div>
    <h2 class="stitle" style="margin-bottom:1.8rem">Frequently asked questions</h2>

    <details class="faq-item">
      <summary class="faq-q">What is the starting price for Windows VPS in Kolkata?</summary>
      <p class="faq-a">KolkataCloud.in offers Windows VPS starting at <strong>₹804/month</strong> (monthly billing). With annual billing, plans start as low as <strong>₹453/month</strong> &mdash; saving you 44%.</p>
    </details>

    <details class="faq-item">
      <summary class="faq-q">Do you provide managed Windows VPS with full RDP access?</summary>
      <p class="faq-a">Yes. All our Windows VPS plans include <strong>full RDP (Remote Desktop Protocol) admin access</strong>, managed security, automated daily backups, DDoS protection, and 24/7 support from our Kolkata-based team.</p>
    </details>

    <details class="faq-item">
      <summary class="faq-q">Can I host Tally or ERP software on your cloud VPS?</summary>
      <p class="faq-a">Absolutely. Our Windows Server 2025 VPS is fully compatible with <strong>Tally Prime, Tally ERP 9</strong>, and all major ERP, accounting, and billing software. Access Tally remotely from anywhere via RDP &mdash; perfect for CA firms and accounting teams in Kolkata.</p>
    </details>

    <details class="faq-item">
      <summary class="faq-q">How quickly will my Windows VPS be set up?</summary>
      <p class="faq-a">Your Windows VPS is provisioned within <strong>15 minutes</strong> of payment confirmation. Our team handles all initial configuration &mdash; firewall, RDP, Windows updates &mdash; so you just connect and get started immediately.</p>
    </details>

    <details class="faq-item">
      <summary class="faq-q">Is KolkataCloud.in based in Kolkata?</summary>
      <p class="faq-a">Yes. We are a <strong>Kolkata-based managed hosting company</strong>. Our support team is located in Kolkata, West Bengal, India, and available Monday to Saturday 9 AM &ndash; 8 PM IST via phone, WhatsApp, and email at sales@kolkatacloud.in.</p>
    </details>

  </div>
</section>

<!-- FOOTER -->
<footer>
  <a href="#" class="flogo">
    <span class="flogo-cloud"><svg width="26" height="17" viewBox="0 0 26 17" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20.8 8.23a7.6 7.6 0 00-14.3-2.58A5.4 5.4 0 005.4 16H20.2a4.8 4.8 0 00.6-9.77z" fill="#1d6fe8"/><path d="M20.8 8.23c-.18 0-.36.01-.54.03A5.4 5.4 0 0015.2 5.5a5.35 5.35 0 00-1.08.11 7.6 7.6 0 016.68 2.62z" fill="#5aabff" opacity=".6"/><ellipse cx="21.5" cy="12.5" rx="3.5" ry="3" fill="#1d6fe8" opacity=".35"/></svg></span>
    KolkataCloud
  </a>
  <nav class="flinks">
    <a href="#features">Features</a>
    <a href="#pricing">Pricing</a>
    <a href="#os-info">Windows VPS</a>
    <a href="#faq">FAQ</a>
    <a href="mailto:{SALES_EMAIL}">Sales</a>
    <a href="mailto:{SUPPORT_EMAIL}">Support</a>
  </nav>
  <p>&copy; {year} KolkataCloud &mdash; All rights reserved.</p>
  <div class="cloudbadge">
    <svg width="18" height="12" viewBox="0 0 26 17" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20.8 8.23a7.6 7.6 0 00-14.3-2.58A5.4 5.4 0 005.4 16H20.2a4.8 4.8 0 00.6-9.77z" fill="#1d6fe8"/><path d="M20.8 8.23c-.18 0-.36.01-.54.03A5.4 5.4 0 0015.2 5.5a5.35 5.35 0 00-1.08.11 7.6 7.6 0 016.68 2.62z" fill="#5aabff" opacity=".7"/><ellipse cx="21.5" cy="12.5" rx="3.5" ry="3" fill="#1d6fe8" opacity=".4"/></svg>
    Cloud&#8209;Powered
  </div>
</footer>

<!-- WhatsApp floating button -->
<a href="{SUPPORT_WA}" target="_blank" rel="noopener" class="wa-float" aria-label="Chat on WhatsApp">
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
  <span class="wa-float-label">Chat with us</span>
</a>

<script>
// ── Nav scroll shrink ─────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {{
  document.getElementById('main-nav').classList.toggle('scrolled', window.scrollY > 40);
}}, {{passive:true}});

// ── Billing toggle ────────────────────────────────────────────────────────────
let currentCycle = 1;
const cycleLabel = {{
  1:'per month, billed monthly', 3:'per month, billed quarterly',
  6:'per month, billed half-yearly', 12:'per month, billed annually',
}};
function setCycle(n) {{
  currentCycle = n;
  document.querySelectorAll('.bt-btn').forEach(b => b.classList.toggle('active', +b.dataset.cycle === n));
  document.querySelectorAll('.plan').forEach(card => {{
    const priceEl = card.querySelector('.plan-price');
    const periodEl = card.querySelector('.plan-period');
    const totalEl = card.querySelector('.plan-total');
    const badgeEl = card.querySelector('.plan-save-badge');
    if (!priceEl) return;
    if (n === 1) {{
      priceEl.textContent = card.dataset.p1;
      periodEl.textContent = cycleLabel[1];
      totalEl.style.display = 'none';
      badgeEl.style.display = 'none';
    }} else {{
      const key = n === 3 ? '3' : n === 6 ? '6' : '12';
      priceEl.textContent = card.dataset['p' + key];
      periodEl.textContent = cycleLabel[n];
      totalEl.textContent = 'Total billed: ' + card.dataset['t' + key];
      totalEl.style.display = 'block';
      badgeEl.textContent = card.dataset['s' + key];
      badgeEl.style.display = 'inline-block';
    }}
  }});
  document.getElementById('annual-banner').classList.toggle('show', n === 12);
}}

// ── Math CAPTCHA ──────────────────────────────────────────────────────────────
let _capAnswer = 0;
function newCaptcha() {{
  const ops = ['+', '-', '\u00d7'];
  const op = ops[Math.floor(Math.random() * ops.length)];
  let a, b, ans;
  if (op === '+') {{ a = rnd(1,20); b = rnd(1,20); ans = a + b; }}
  else if (op === '-') {{ a = rnd(5,25); b = rnd(1, a); ans = a - b; }}
  else {{ a = rnd(2,9); b = rnd(2,9); ans = a * b; }}
  _capAnswer = ans;
  document.getElementById('cap-q').textContent = a + ' ' + op + ' ' + b;
  document.getElementById('cap-ans').value = '';
}}
function rnd(lo, hi) {{ return Math.floor(Math.random() * (hi - lo + 1)) + lo; }}
newCaptcha();

// ── Enquiry submit ────────────────────────────────────────────────────────────
function submitEnquiry() {{
  const name = document.getElementById('f-name').value.trim();
  const phone = document.getElementById('f-phone').value.trim();
  const email = document.getElementById('f-email').value.trim();
  const plan = document.getElementById('f-plan').value;
  const msg = document.getElementById('f-msg').value.trim();
  const capIn = parseInt(document.getElementById('cap-ans').value, 10);
  const out = document.getElementById('form-msg');
  out.className = 'form-msg'; out.textContent = '';
  if (!name || !phone || !email) {{
    out.textContent = 'Please fill in Name, Phone, and Email before submitting.';
    out.className = 'form-msg err'; return;
  }}
  if (isNaN(capIn) || capIn !== _capAnswer) {{
    out.textContent = 'Incorrect security answer. Please try again.';
    out.className = 'form-msg err'; newCaptcha(); return;
  }}
  fetch('/enquiry', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ name, phone, email, plan, message: msg, captcha_answer: capIn, captcha_expected: _capAnswer }})
  }})
  .then(r => r.json())
  .then(data => {{
    if (data.ok) {{
      out.textContent = '\u2713 Enquiry sent! Our team will contact you within 2 hours.';
      out.className = 'form-msg ok';
      ['f-name','f-phone','f-email','f-msg'].forEach(id => document.getElementById(id).value = '');
      document.getElementById('f-plan').selectedIndex = 0;
      newCaptcha();
    }} else {{ throw new Error(data.error || 'Server error'); }}
  }})
  .catch(() => {{
    const subject = encodeURIComponent('VPS Enquiry from ' + name + ' - ' + (plan || 'General'));
    const body = encodeURIComponent('Name: ' + name + '\\nPhone: ' + phone + '\\nEmail: ' + email + '\\nPlan: ' + (plan || 'Not selected') + '\\n\\nMessage:\\n' + msg);
    window.location.href = 'mailto:{SUPPORT_EMAIL}?subject=' + subject + '&body=' + body;
    out.textContent = 'Opening your mail client\u2026 If nothing opens, email us at {SUPPORT_EMAIL}';
    out.className = 'form-msg ok'; newCaptcha();
  }});
}}
</script>
</body>
</html>"""


def create_flask_app():
    if not HAS_FLASK:
        return None

    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "kc-dev-secret-change-me")

    @app.route("/")
    def index() -> Response:
        return Response(render_page(), mimetype="text/html")

    @app.route("/sitemap.xml")
    def sitemap() -> Response:
        from datetime import date
        today = date.today().isoformat()
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://kolkatacloud.in/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://kolkatacloud.in/#pricing</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>
  <url><loc>https://kolkatacloud.in/#features</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://kolkatacloud.in/#os-info</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>
  <url><loc>https://kolkatacloud.in/#faq</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>
  <url><loc>https://kolkatacloud.in/#contact</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>
</urlset>"""
        return Response(xml, mimetype="application/xml")

    @app.route("/robots.txt")
    def robots() -> Response:
        return Response(
            "User-agent: *\nAllow: /\nDisallow: /enquiry\nSitemap: https://kolkatacloud.in/sitemap.xml\n",
            mimetype="text/plain"
        )

    @app.route("/og-image.png")
    def og_image() -> Response:
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
  <rect width="1200" height="630" fill="#0b0d11"/>
  <text x="600" y="270" text-anchor="middle" font-family="sans-serif" font-size="80" font-weight="bold" fill="#ffffff">KolkataCloud<tspan fill="#1d6fe8">.in</tspan></text>
  <text x="600" y="370" text-anchor="middle" font-family="sans-serif" font-size="34" fill="#6b7280">Managed Windows VPS · India · From ₹453/mo</text>
  <text x="600" y="430" text-anchor="middle" font-family="sans-serif" font-size="26" fill="#1d6fe8">sales@kolkatacloud.in · +91-8653436887</text>
</svg>"""
        return Response(svg, mimetype="image/svg+xml")

    @app.route("/enquiry", methods=["POST"])
    def enquiry() -> Response:
        data    = request.get_json(force=True) or {}
        name    = data.get("name", "").strip()
        phone   = data.get("phone", "").strip()
        email   = data.get("email", "").strip()
        plan    = data.get("plan", "Not selected")
        message = data.get("message", "").strip()
        cap_in  = data.get("captcha_answer")
        cap_exp = data.get("captcha_expected")

        if not (name and phone and email):
            return jsonify(ok=False, error="Missing required fields"), 400
        try:
            if int(cap_in) != int(cap_exp):
                return jsonify(ok=False, error="Captcha verification failed"), 400
        except (TypeError, ValueError):
            return jsonify(ok=False, error="Invalid captcha"), 400

        subject = f"[KolkataCloud] VPS Enquiry from {name} \u2014 Plan: {plan}"
        body = (
            f"New enquiry via KolkataCloud.in\n{'='*50}\n"
            f"Name    : {name}\nPhone   : {phone}\nEmail   : {email}\nPlan    : {plan}\n"
            f"{'='*50}\nMessage :\n{message or '(none)'}\n"
        )

        try:
            msg_obj = MIMEMultipart()
            msg_obj["From"]     = SMTP_USER
            msg_obj["To"]       = f"{SALES_EMAIL}, {SUPPORT_EMAIL}"
            msg_obj["Subject"]  = subject
            msg_obj["Reply-To"] = email
            msg_obj.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as srv:
                srv.starttls()
                srv.login(SMTP_USER, SMTP_PASS)
                srv.sendmail(SMTP_USER, [SALES_EMAIL, SUPPORT_EMAIL], msg_obj.as_string())
            return jsonify(ok=True)
        except Exception as ex:
            print(f"[MAIL ERROR] {ex}")
            return jsonify(ok=False, error=str(ex)), 500

    return app


app = create_flask_app()

if __name__ == "__main__":
    if app:
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting server on port {port}  (Python {sys.version})")
        print(f"  Sales mail  : {SALES_EMAIL}")
        print(f"  Support mail: {SUPPORT_EMAIL}")
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        out = "index.html"
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(render_page())
        print(f"Written to {out}  (Python {sys.version})")
        print("Install Flask (`pip install flask`) to run as a live server.")
