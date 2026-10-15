#!/usr/bin/env python3
"""
estimate.py - Run the BigQuery-to-Snowflake cost estimate and build the HTML report.

Usage:
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/estimate.py \
        --csv <DIR_OR_FILES...> --inputs inputs.json --tags project_tags.json \
        --start 2026-03-01 --end 2026-10-01 --out <REPORT.html> [--results <results.json>]

--start is the first day of the first month; --end is the first day of the month after the
last month (exclusive). The example covers March through September.

inputs.json keys (see SKILL.md Step 2):
    customer, initial_storage_tb, tt_fs_pct, price_per_tb, storage_growth (list of 3),
    price_per_credit, compute_growth (list of 3), low_factor, high_factor
project_tags.json: {"<project_id>": "RES" | "OD", ...}
"""

import argparse
import calendar
import csv
import html
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

# Fixed for every customer - never prompted.
HOURS_PER_MONTH = 730
SLOTS_PER_XS_NODE = 16
CREDITS_PER_XS_NODE_HOUR = 1
PROJECTION_MONTHS = 36
SLOT_CALCULATOR_URL = "https://app.snowflake.com/streamlit/sfcogsops/snowhouse_aws_us_west_2/#/apps/icosbexzbmbas7a4gzfw"

DEFAULTS = {
    "tt_fs_pct": 0.0,
    "price_per_tb": 23.00,
    "storage_growth": [0.127, 0.127, 0.127],
    "price_per_credit": 4.00,
    "compute_growth": [0.05, 0.05, 0.05],
    "low_factor": 0.80,
    "high_factor": 1.20,
}
REQUIRED_COLS = ["project_id", "year_month", "total_slot_ms", "active_minutes_in_month",
                 "pct_of_month_active"]
TRACKS = ["RES", "OD"]
TRACK_NAMES = {"RES": "Reserved slots", "OD": "On-demand", "COMBINED": "Combined",
               "STORAGE": "Storage"}


# ---------------------------------------------------------------- loading / validation

def expected_months(start: str, end: str) -> list[str]:
    """start = first day of first month; end = first day of the month after the last (exclusive)."""
    s, e = date.fromisoformat(start), date.fromisoformat(end)
    if s.day != 1 or e.day != 1:
        sys.exit("Error: --start and --end must be the first day of a month (YYYY-MM-01)")
    if e <= s:
        sys.exit("Error: --end must be after --start")
    out, y, m = [], s.year, s.month
    while date(y, m, 1) < e:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def to_float(value) -> float:
    try:
        return float(str(value).replace(",", "")) if str(value).strip() else 0.0
    except ValueError:
        sys.exit(f"Error: expected a number, got '{value}'")


def load_csvs(paths: list[str]) -> list[dict]:
    """Read every CSV into a list of row dicts (lower-case column names)."""
    files = []
    for p in paths:
        pp = Path(p)
        files.extend(sorted(pp.glob("*.csv")) if pp.is_dir() else [pp])
    if not files:
        sys.exit("Error: no CSV files found")
    rows = []
    for f in files:
        with open(f, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            cols = [c.strip().lower() for c in (reader.fieldnames or [])]
            missing = [c for c in REQUIRED_COLS if c not in cols]
            if missing:
                sys.exit(f"Error: {f.name} is missing required columns: {', '.join(missing)}")
            for raw in reader:
                r = {k.strip().lower(): v for k, v in raw.items() if k}
                rows.append({"project_id": str(r["project_id"]).strip(),
                             "year_month": str(r["year_month"]).strip()[:7],
                             "total_slot_ms": to_float(r["total_slot_ms"]),
                             "active_minutes_in_month": to_float(r["active_minutes_in_month"]),
                             "source_file": f.name})
    return rows


def validate(rows: list[dict], months: list[str], tags: dict) -> list[str]:
    errors = []
    found = sorted({r["year_month"] for r in rows})
    missing = [m for m in months if m not in found]
    extra = [m for m in found if m not in months]
    if missing:
        errors.append(f"Missing months: {', '.join(missing)}")
    if extra:
        errors.append(f"Months outside the requested range: {', '.join(extra)}")
    files_by_month = defaultdict(set)
    for r in rows:
        files_by_month[r["year_month"]].add(r["source_file"])
    dup = sorted(m for m, fs in files_by_month.items() if len(fs) > 1)
    if dup:
        errors.append("Month(s) found in more than one file: " + ", ".join(dup))
    pairs = Counter((r["project_id"], r["year_month"]) for r in rows)
    n_dup = sum(c - 1 for c in pairs.values() if c > 1)
    if n_dup:
        errors.append(f"{n_dup} duplicate project/month rows")
    untagged = sorted({r["project_id"] for r in rows} - set(tags))
    if untagged:
        errors.append("Projects not tagged RES/OD: " + ", ".join(untagged))
    bad = {p: t for p, t in tags.items() if t not in TRACKS}
    if bad:
        errors.append(f"Invalid tags (must be RES or OD): {bad}")
    return errors


def minutes_in_month(ym: str) -> int:
    y, m = (int(x) for x in ym.split("-"))
    return calendar.monthrange(y, m)[1] * 24 * 60


# ---------------------------------------------------------------- calculations

def monthly_rate(annual: float) -> float:
    return (1 + annual) ** (1 / 12) - 1


def calculate(rows: list[dict], months: list[str], tags: dict, inp: dict) -> dict:
    # Step 1 - utilization per track over every active project-month
    util = {}
    for t in TRACKS:
        sub = [r for r in rows if tags[r["project_id"]] == t]
        active = sum(r["active_minutes_in_month"] for r in sub)
        total = float(sum(minutes_in_month(r["year_month"]) for r in sub))
        util[t] = {"active_minutes": active, "total_minutes": total,
                   "pct": active / total if total else 0.0,
                   "project_months": len(sub)}

    slot_ms_by = defaultdict(float)
    for r in rows:
        slot_ms_by[(tags[r["project_id"]], r["year_month"])] += r["total_slot_ms"]

    # Steps 2-6 - per track, per month
    monthly = []
    for m in months:
        for t in TRACKS:
            slot_ms = slot_ms_by[(t, m)]
            slot_hours = slot_ms / 3_600_000
            avg_slots = slot_hours / HOURS_PER_MONTH
            xs_nodes = avg_slots / SLOTS_PER_XS_NODE
            credits = xs_nodes * CREDITS_PER_XS_NODE_HOUR * HOURS_PER_MONTH * util[t]["pct"]
            monthly.append({"month": m, "track": t, "slot_ms": slot_ms, "slot_hours": slot_hours,
                            "avg_slots": avg_slots, "xs_nodes": xs_nodes, "credits": credits,
                            "cost": credits * inp["price_per_credit"]})

    # Steps 7-8 - average across the observation period, then combine
    n_months = len(months)
    track_credits = {t: sum(x["credits"] for x in monthly if x["track"] == t) for t in TRACKS}
    avg_credits = {t: track_credits[t] / n_months for t in TRACKS}
    starting_credits = avg_credits["RES"] + avg_credits["OD"]

    # Steps 9-12 - 36-month projection
    s_rates = [monthly_rate(g) for g in inp["storage_growth"]]
    c_rates = [monthly_rate(g) for g in inp["compute_growth"]]
    month1_tb = inp["initial_storage_tb"] * (1 + inp["tt_fs_pct"])
    proj, tb, cr = [], month1_tb, starting_credits
    for n in range(1, PROJECTION_MONTHS + 1):
        yi = (n - 1) // 12
        if n > 1:
            tb *= 1 + s_rates[yi]
            cr *= 1 + c_rates[yi]
        proj.append({"month": n, "year": yi + 1, "storage_tb": tb,
                     "storage_cost": tb * inp["price_per_tb"], "credits": cr,
                     "compute_cost": cr * inp["price_per_credit"]})

    # Steps 13-14 - annual totals and range
    years = []
    for y in (1, 2, 3):
        sub = [x for x in proj if x["year"] == y]
        st, co = sum(x["storage_cost"] for x in sub), sum(x["compute_cost"] for x in sub)
        tot = st + co
        years.append({"year": y, "storage": st, "compute": co, "total": tot,
                      "low": tot * inp["low_factor"], "high": tot * inp["high_factor"],
                      "credits": sum(x["credits"] for x in sub),
                      "end_tb": sub[-1]["storage_tb"]})

    return {"util": util, "monthly": monthly, "track_credits": track_credits, "avg_credits": avg_credits,
            "starting_credits": starting_credits, "s_rates": s_rates, "c_rates": c_rates,
            "month1_tb": month1_tb, "projection": proj, "years": years, "n_months": n_months}


# ---------------------------------------------------------------- formatting helpers

def money(x, dp=0):
    return f"${x:,.{dp}f}"


def num(x, dp=0):
    return f"{x:,.{dp}f}"


def pct(x, dp=1):
    return f"{x * 100:.{dp}f}%"


def esc(s):
    return html.escape(str(s))


def badge(track):
    return f'<span class="badge b-{track.lower()}">{esc(track)}</span>'


def month_label(ym: str) -> str:
    y, m = (int(x) for x in ym.split("-"))
    return date(y, m, 1).strftime("%b %Y")


# ---------------------------------------------------------------- SVG charts

def svg_stacked_bars(series: list[dict], labels: list[str], height=260, label_every=1,
                     value_fmt=lambda v: money(v)) -> str:
    """series: [{"name":..., "cls":..., "values":[...]}] stacked bottom-up."""
    n = len(labels)
    W, H, pl, pb, pt = 760, height, 70, 34, 12
    plot_w, plot_h = W - pl - 10, H - pb - pt
    totals = [sum(s["values"][i] for s in series) for i in range(n)]
    vmax = max(totals) * 1.08 if totals and max(totals) > 0 else 1
    bw = plot_w / n
    parts = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(5):
        v = vmax * k / 4
        y = pt + plot_h - plot_h * k / 4
        parts.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{W - 10}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'<text x="{pl - 6}" y="{y + 4:.1f}" class="axis" text-anchor="end">{esc(value_fmt(v))}</text>')
    for i in range(n):
        x = pl + i * bw + bw * 0.15
        y_base = pt + plot_h
        for s in series:
            h = plot_h * s["values"][i] / vmax
            y_base -= h
            parts.append(f'<rect x="{x:.1f}" y="{y_base:.1f}" width="{bw * 0.7:.1f}" height="{h:.1f}" '
                         f'class="{s["cls"]}"><title>{esc(labels[i])} - {esc(s["name"])}: '
                         f'{esc(value_fmt(s["values"][i]))}</title></rect>')
        if i % label_every == 0:
            parts.append(f'<text x="{x + bw * 0.35:.1f}" y="{H - 14}" class="axis" '
                         f'text-anchor="middle">{esc(labels[i])}</text>')
    parts.append("</svg>")
    legend = "".join(f'<span class="leg"><i class="{s["cls"]}"></i>{esc(s["name"])}</span>' for s in series)
    return f'<div class="chart-wrap">{"".join(parts)}</div><div class="legend">{legend}</div>'


# ---------------------------------------------------------------- HTML report

CSS = """
:root { color-scheme: light dark;
  --res: #2563eb; --od: #ea580c; --comb: #7c3aed; --stor: #0d9488;
  --border: light-dark(#d1d5db, #374151); --muted: light-dark(#6b7280, #9ca3af);
  --card: light-dark(#f9fafb, #111827); --head: light-dark(#f3f4f6, #1f2937); }
* { box-sizing: border-box; }
body { font-family: -apple-system, system-ui, "Segoe UI", sans-serif; max-width: 980px; width: 100%;
  margin: 0 auto; padding: clamp(16px, 4vw, 28px); color: light-dark(#1f2937, #e5e7eb);
  background: light-dark(#ffffff, #030712); line-height: 1.5; }
h1 { font-size: 1.6rem; margin: 0 0 4px; color: light-dark(#0f172a, #f1f5f9); }
h2 { font-size: 1.2rem; margin: 36px 0 10px; padding-bottom: 6px; border-bottom: 2px solid var(--border);
  color: light-dark(#0f172a, #f1f5f9); }
h3 { font-size: 1rem; margin: 18px 0 6px; }
.sub { color: var(--muted); margin: 0 0 18px; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }
.kpi { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
.kpi .l { font-size: .78rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
.kpi .v { font-size: 1.45rem; font-weight: 700; }
.kpi .r { font-size: .82rem; color: var(--muted); }
.table-wrap { overflow-x: auto; margin: 10px 0 16px; }
table { border-collapse: collapse; width: 100%; font-size: .9rem; }
th, td { border: 1px solid var(--border); padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: var(--head); font-weight: 600; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.total td { font-weight: 700; background: var(--head); }
tr.calc td { font-weight: 700; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: .72rem; font-weight: 700;
  color: #fff; letter-spacing: .03em; }
.b-res { background: var(--res); } .b-od { background: var(--od); }
.b-combined { background: var(--comb); } .b-storage { background: var(--stor); }
.tag-default { color: var(--muted); } .tag-override { color: var(--od); font-weight: 600; }
.step { border: 1px solid var(--border); border-left: 5px solid var(--border); border-radius: 8px;
  padding: 10px 14px; margin: 10px 0; background: var(--card); }
.step.res { border-left-color: var(--res); } .step.od { border-left-color: var(--od); }
.step.combined { border-left-color: var(--comb); } .step.storage { border-left-color: var(--stor); }
.step .hdr { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-weight: 600; }
.step .num { color: var(--muted); font-variant-numeric: tabular-nums; }
.step dl { display: grid; grid-template-columns: 90px 1fr; gap: 2px 10px; margin: 8px 0 0; font-size: .9rem; }
.step dt { color: var(--muted); }
.step dd { margin: 0; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .86em;
  background: light-dark(#eef2ff, #1e1b4b); padding: 1px 5px; border-radius: 4px; }
.result { font-weight: 700; }
.phase { margin-top: 22px; font-size: .8rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.chart-wrap { width: 100%; overflow-x: auto; }
svg.chart { width: 100%; min-width: 520px; height: auto; display: block; }
svg .grid { stroke: var(--border); stroke-width: 1; }
svg .axis { fill: var(--muted); font-size: 11px; }
svg .c-compute { fill: var(--comb); } svg .c-storage { fill: var(--stor); }
svg .c-res { fill: var(--res); } svg .c-od { fill: var(--od); }
.legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: .85rem; margin: 4px 0 12px; }
.leg i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }
.leg i.c-compute { background: var(--comb); } .leg i.c-storage { background: var(--stor); }
.leg i.c-res { background: var(--res); } .leg i.c-od { background: var(--od); }
ul.caveats li { margin-bottom: 6px; }
.note { font-size: .85rem; color: var(--muted); }
.callout { border: 1px solid var(--od); border-left: 5px solid var(--od); border-radius: 8px; padding: 10px 14px;
  margin: 0 0 18px; background: light-dark(#fff7ed, #1c1206); font-size: .92rem; }
"""


def build_html(r: dict, rows: list[dict], months: list[str], tags: dict, inp: dict,
               overridden: set, generated: str) -> str:
    cust = inp.get("customer") or "Customer"
    yrs = r["years"]
    pdf = r["projection"]
    first = months[0]
    m0 = {x["track"]: x for x in r["monthly"] if x["month"] == first}
    source_files = sorted({x["source_file"] for x in rows})
    n_projects = len({x["project_id"] for x in rows})

    def src_tag(key):
        return ('<span class="tag-override">Customer value</span>' if key in overridden
                else '<span class="tag-default">Default</span>')

    out = []
    # ---- head
    meta = {
        "generated": generated,
        "intent": f"BigQuery to Snowflake cost estimate for {cust}",
        "dataSources": [{"type": "file", "description": "BigQuery INFORMATION_SCHEMA.JOBS monthly usage exports (CSV)",
                         "files": source_files}],
        "parameters": {**{k: inp[k] for k in DEFAULTS}, "initial_storage_tb": inp["initial_storage_tb"],
                       "observation_months": months, "project_tags": tags},
        "sections": [
            {"id": "summary", "title": "Estimate summary"},
            {"id": "inputs", "title": "Inputs"},
            {"id": "source-data", "title": "Source data"},
            {"id": "walkthrough", "title": "Calculation walkthrough"},
            {"id": "projection", "title": "36-month projection"},
            {"id": "caveats", "title": "Assumptions and caveats"}],
        "producerNotes": "Generated by bigquery-to-snowflake-estimate/scripts/estimate.py. Re-run the script "
                         "with the same CSVs, inputs.json, and project_tags.json to refresh.",
    }
    meta_json = json.dumps(meta, indent=2).replace("</", "<\\/")
    out.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="snowflake-source" content="cortex-agent-authored" />
<title>{esc(cust)} - BigQuery to Snowflake Cost Estimate</title>
<script type="application/json" id="snowflake-report-metadata">
{meta_json}
</script>
<style>{CSS}</style>
</head>
<body>
<h1>{esc(cust)}: BigQuery to Snowflake Cost Estimate</h1>
<p class="sub">Based on {r['n_months']} months of BigQuery usage ({month_label(months[0])} to {month_label(months[-1])}),
{n_projects} projects. Generated {esc(generated)}.</p>
<div class="callout"><strong>This report explains the calculations. It is not the official estimate.</strong>
Use the <a href="{SLOT_CALCULATOR_URL}">Google Slot Calculator</a> Streamlit app for official estimates.</div>
""")

    # ---- 1. Summary
    out.append('<h2 id="summary">Estimate summary</h2><div class="kpis">')
    for y in yrs:
        out.append(f'<div class="kpi"><div class="l">Year {y["year"]} estimate</div>'
                   f'<div class="v">{money(y["total"])}</div>'
                   f'<div class="r">Range {money(y["low"])} to {money(y["high"])}</div></div>')
    out.append("</div>")
    out.append('<div class="table-wrap"><table><thead><tr><th></th>'
               + "".join(f'<th class="n">Year {y["year"]}</th>' for y in yrs) + "</tr></thead><tbody>")
    out.append(f'<tr><td>Low ({pct(inp["low_factor"], 0)})</td>' + "".join(f'<td class="n">{money(y["low"])}</td>' for y in yrs) + "</tr>")
    out.append('<tr class="calc"><td>Calculated</td>' + "".join(f'<td class="n">{money(y["total"])}</td>' for y in yrs) + "</tr>")
    out.append(f'<tr><td>High ({pct(inp["high_factor"], 0)})</td>' + "".join(f'<td class="n">{money(y["high"])}</td>' for y in yrs) + "</tr>")
    out.append("</tbody></table></div>")
    out.append('<div class="table-wrap"><table><thead><tr><th>Component (calculated)</th>'
               + "".join(f'<th class="n">Year {y["year"]}</th>' for y in yrs) + "</tr></thead><tbody>")
    out.append("<tr><td>Compute</td>" + "".join(f'<td class="n">{money(y["compute"])}</td>' for y in yrs) + "</tr>")
    out.append("<tr><td>Storage</td>" + "".join(f'<td class="n">{money(y["storage"])}</td>' for y in yrs) + "</tr>")
    out.append('<tr class="total"><td>Total</td>' + "".join(f'<td class="n">{money(y["total"])}</td>' for y in yrs) + "</tr>")
    out.append("<tr><td>Credits consumed</td>" + "".join(f'<td class="n">{num(y["credits"])}</td>' for y in yrs) + "</tr>")
    out.append("<tr><td>Storage at year end (TB)</td>" + "".join(f'<td class="n">{num(y["end_tb"], 1)}</td>' for y in yrs) + "</tr>")
    out.append("</tbody></table></div>")

    # ---- 2. Inputs
    out.append('<h2 id="inputs">Inputs</h2><div class="table-wrap"><table><thead><tr>'
               '<th>Input</th><th class="n">Value</th><th>Source</th></tr></thead><tbody>')
    input_rows = [
        ("Initial storage volume", f'{num(inp["initial_storage_tb"], 1)} TB', '<span class="tag-override">Customer value</span>'),
        ("Time travel / failsafe", pct(inp["tt_fs_pct"]), src_tag("tt_fs_pct")),
        ("Price per TB (per month)", money(inp["price_per_tb"], 2), src_tag("price_per_tb")),
        *[(f"Storage growth - Year {i + 1}", pct(g), src_tag("storage_growth")) for i, g in enumerate(inp["storage_growth"])],
        ("Price per credit", money(inp["price_per_credit"], 2), src_tag("price_per_credit")),
        *[(f"Compute growth - Year {i + 1}", pct(g), src_tag("compute_growth")) for i, g in enumerate(inp["compute_growth"])],
        ("Low / high range factors", f'{inp["low_factor"]:.2f} / {inp["high_factor"]:.2f}',
         src_tag("low_factor") if "low_factor" in overridden else src_tag("high_factor")),
        ("Hours per month", num(HOURS_PER_MONTH), '<span class="tag-default">Fixed</span>'),
        ("Slot-to-node comparison", f"{SLOTS_PER_XS_NODE} BigQuery slots = 1 X-Small Snowflake node", '<span class="tag-default">Fixed</span>'),
    ]
    for label, val, src in input_rows:
        out.append(f'<tr><td>{esc(label)}</td><td class="n">{esc(val)}</td><td>{src}</td></tr>')
    out.append("</tbody></table></div>")

    # ---- 3. Source data
    out.append('<h2 id="source-data">Source data</h2>')
    out.append(f'<p>{r["n_months"]} monthly exports, {len(rows)} project-month rows. '
               f'Each project is tagged as reserved slots ({badge("RES")}) or on-demand ({badge("OD")}).</p>')
    proj = defaultdict(lambda: {"months": set(), "slot_ms": 0.0, "active": 0.0})
    for x in rows:
        p = proj[x["project_id"]]
        p["months"].add(x["year_month"])
        p["slot_ms"] += x["total_slot_ms"]
        p["active"] += x["active_minutes_in_month"]
    out.append('<div class="table-wrap"><table><thead><tr><th>Project</th><th>Track</th>'
               '<th class="n">Months with activity</th><th class="n">Slot hours (total)</th>'
               '<th class="n">Active hours (total)</th></tr></thead><tbody>')
    for pid, row in sorted(proj.items(), key=lambda kv: kv[1]["slot_ms"], reverse=True):
        out.append(f'<tr><td>{esc(pid)}</td><td>{badge(tags[pid])}</td><td class="n">{len(row["months"])}</td>'
                   f'<td class="n">{num(row["slot_ms"] / 3_600_000)}</td><td class="n">{num(row["active"] / 60, 1)}</td></tr>')
    out.append("</tbody></table></div>")
    rc = Counter(x["year_month"] for x in rows)
    out.append('<div class="table-wrap"><table><thead><tr><th>Month</th><th class="n">Projects (rows)</th>'
               '<th>File</th></tr></thead><tbody>')
    for m in months:
        f = ", ".join(sorted({x["source_file"] for x in rows if x["year_month"] == m}))
        out.append(f'<tr><td>{month_label(m)}</td><td class="n">{rc.get(m, 0)}</td><td>{esc(f)}</td></tr>')
    out.append("</tbody></table></div>")

    # ---- 4. Walkthrough
    out.append('<h2 id="walkthrough">Calculation walkthrough</h2>')
    out.append(f'<p class="note">Each step shows the formula, the numbers plugged in, and the result. Steps 2-6 run for every '
               f'observed month. The worked example uses {month_label(first)}.</p>')

    def step(order, track, title, formula, plugged, result):
        out.append(f'<div class="step {track.lower()}"><div class="hdr"><span class="num">{esc(order)}</span>'
                   f'{badge(track)}<span>{esc(title)}</span></div><dl>'
                   f'<dt>Formula</dt><dd><code>{esc(formula)}</code></dd>'
                   f'<dt>Plugged in</dt><dd><code>{esc(plugged)}</code></dd>'
                   f'<dt>Result</dt><dd class="result">{esc(result)}</dd></dl></div>')

    out.append('<div class="phase">Part 1 - Compute: each track calculated separately</div>')
    for t, o in (("RES", "1a"), ("OD", "1b")):
        u = r["util"][t]
        step(o, t, f"Utilization % ({TRACK_NAMES[t]})",
             "Active Minutes / Total Minutes (across all active project-months)",
             f'{num(u["active_minutes"])} / {num(u["total_minutes"])}', pct(u["pct"]))
    for t, o in (("RES", "2a"), ("OD", "2b")):
        step(o, t, "Slot hours", "Slot ms / 3,600,000",
             f'{num(m0[t]["slot_ms"])} / 3,600,000', f'{num(m0[t]["slot_hours"], 1)} slot hours ({month_label(first)})')
    for t, o in (("RES", "3a"), ("OD", "3b")):
        step(o, t, "Average slots", "Slot Hours / Hours per Month",
             f'{num(m0[t]["slot_hours"], 1)} / {HOURS_PER_MONTH}', f'{num(m0[t]["avg_slots"], 2)} slots')
    for t, o in (("RES", "4a"), ("OD", "4b")):
        step(o, t, "Equivalent X-Small nodes", "Average Slots / 16 slots per X-Small node",
             f'{num(m0[t]["avg_slots"], 2)} / {SLOTS_PER_XS_NODE}', f'{num(m0[t]["xs_nodes"], 2)} X-Small nodes')
    for t, o in (("RES", "5a"), ("OD", "5b")):
        step(o, t, "Credits per month",
             "X-Small Nodes x 1 credit/hr x Hours per Month x Utilization %",
             f'{num(m0[t]["xs_nodes"], 2)} x 1 x {HOURS_PER_MONTH} x {pct(r["util"][t]["pct"])}',
             f'{num(m0[t]["credits"])} credits')
    for t, o in (("RES", "6a"), ("OD", "6b")):
        step(o, t, "Monthly compute cost", "Credits per Month x Price per Credit",
             f'{num(m0[t]["credits"])} x {money(inp["price_per_credit"], 2)}', money(m0[t]["cost"]))
    for t, o in (("RES", "7a"), ("OD", "7b")):
        tot = r["track_credits"][t]
        step(o, t, "Average monthly credits", "SUM(Monthly Credits) / # Months Observed",
             f'{num(tot)} / {r["n_months"]}', f'{num(r["avg_credits"][t])} credits/month')
    step("8", "COMBINED", "Starting monthly credits", "Avg Monthly Credits RES + Avg Monthly Credits OD",
         f'{num(r["avg_credits"]["RES"])} + {num(r["avg_credits"]["OD"])}', f'{num(r["starting_credits"])} credits/month')

    out.append('<div class="phase">Part 2 - Storage</div>')
    step("9", "STORAGE", "Month 1 storage", "Initial Storage x (1 + Time Travel / Failsafe %)",
         f'{num(inp["initial_storage_tb"], 1)} TB x (1 + {pct(inp["tt_fs_pct"])})', f'{num(r["month1_tb"], 1)} TB')
    sr = ", ".join(f"Y{i + 1} {pct(g)} -> {pct(m, 3)}/mo" for i, (g, m) in enumerate(zip(inp["storage_growth"], r["s_rates"])))
    step("10", "STORAGE", "Monthly storage growth (36 months)",
         "Month N TB = Month N-1 TB x (1 + monthly rate for that year); monthly rate = (1 + annual)^(1/12) - 1",
         sr, f'{num(pdf[-1]["storage_tb"], 1)} TB in month 36')
    step("11", "STORAGE", "Monthly storage cost", "Month N TB x Price per TB",
         f'{num(r["month1_tb"], 1)} TB x {money(inp["price_per_tb"], 2)} (month 1)',
         f'{money(pdf[0]["storage_cost"])} in month 1, {money(pdf[-1]["storage_cost"])} in month 36')

    out.append('<div class="phase">Part 3 - Multi-year projection</div>')
    cr = ", ".join(f"Y{i + 1} {pct(g)} -> {pct(m, 3)}/mo" for i, (g, m) in enumerate(zip(inp["compute_growth"], r["c_rates"])))
    step("12", "COMBINED", "Monthly compute growth (36 months)",
         "Month N Credits = Month N-1 Credits x (1 + monthly rate for that year); Cost = Credits x Price per Credit",
         cr, f'{num(pdf[-1]["credits"])} credits ({money(pdf[-1]["compute_cost"])}) in month 36')
    step("13", "COMBINED", "Annual totals", "SUM of monthly storage + compute cost for months 1-12, 13-24, 25-36",
         "; ".join(f'Y{y["year"]}: {money(y["storage"])} + {money(y["compute"])}' for y in yrs),
         "; ".join(f'Y{y["year"]} {money(y["total"])}' for y in yrs))
    step("14", "COMBINED", "Low / high range", "Total x Low Range Factor / Total x High Range Factor",
         f'x {inp["low_factor"]:.2f} / x {inp["high_factor"]:.2f}',
         "; ".join(f'Y{y["year"]} {money(y["low"])} - {money(y["high"])}' for y in yrs))

    # ---- 6. Projection
    out.append('<h2 id="projection">36-month projection</h2>')
    out.append(svg_stacked_bars(
        [{"name": "Compute", "cls": "c-compute", "values": [x["compute_cost"] for x in pdf]},
         {"name": "Storage", "cls": "c-storage", "values": [x["storage_cost"] for x in pdf]}],
        [f"M{x['month']}" for x in pdf], label_every=3))
    out.append('<div class="table-wrap"><table><thead><tr><th>Month</th><th>Year</th><th class="n">Credits</th>'
               '<th class="n">Compute cost</th><th class="n">Storage (TB)</th><th class="n">Storage cost</th>'
               '<th class="n">Total</th></tr></thead><tbody>')
    for x in pdf:
        out.append(f'<tr><td>{int(x["month"])}</td><td>{int(x["year"])}</td><td class="n">{num(x["credits"])}</td>'
                   f'<td class="n">{money(x["compute_cost"])}</td><td class="n">{num(x["storage_tb"], 1)}</td>'
                   f'<td class="n">{money(x["storage_cost"])}</td>'
                   f'<td class="n">{money(x["compute_cost"] + x["storage_cost"])}</td></tr>')
        if int(x["month"]) % 12 == 0:
            y = yrs[int(x["year"]) - 1]
            out.append(f'<tr class="total"><td colspan="2">Year {y["year"]} total</td><td class="n">{num(y["credits"])}</td>'
                       f'<td class="n">{money(y["compute"])}</td><td class="n"></td><td class="n">{money(y["storage"])}</td>'
                       f'<td class="n">{money(y["total"])}</td></tr>')
    out.append("</tbody></table></div>")

    # ---- 7. Caveats
    out.append('<h2 id="caveats">Assumptions and caveats</h2><ul class="caveats">')
    for c in [
        f"16 BigQuery slots = 1 X-Small Snowflake node is a hardware comparison, not an exact performance match. "
        f"Actual throughput varies by workload (ETL, BI, ad hoc).",
        f"The baseline averages {r['n_months']} months of usage. Short observation periods, one-time loads, or "
        f"seasonal peaks outside the window make the estimate less reliable.",
        "Utilization % is calculated across every project-month that had activity. Months where a project ran "
        "no queries are not included.",
        "Prices are " + ("customer contract values." if {"price_per_credit", "price_per_tb"} <= overridden
                         else "list-price defaults unless marked as customer values in Inputs."),
        f"The {pct(inp['low_factor'], 0)} / {pct(inp['high_factor'], 0)} range reflects estimation uncertainty "
        f"and should be widened if the source data is incomplete.",
    ]:
        out.append(f"<li>{esc(c)}</li>")
    out.append("</ul></body></html>")
    return "\n".join(out)


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="BigQuery to Snowflake cost estimate")
    p.add_argument("--csv", nargs="+", required=True, help="CSV files or a directory of CSVs")
    p.add_argument("--inputs", required=True, help="inputs.json")
    p.add_argument("--tags", required=True, help="project_tags.json mapping project_id -> RES|OD")
    p.add_argument("--start", required=True, help="First day of the first month, YYYY-MM-01")
    p.add_argument("--end", required=True, help="First day of the month after the last month, YYYY-MM-01 (exclusive)")
    p.add_argument("--out", required=True, help="Output HTML path")
    p.add_argument("--results", help="Optional JSON file with all calculated values")
    p.add_argument("--validate-only", action="store_true", help="Validate CSVs and tags, then exit")
    args = p.parse_args()

    raw = json.loads(Path(args.inputs).read_text())
    inp = {**DEFAULTS, **raw}
    if "initial_storage_tb" not in inp:
        sys.exit("Error: inputs.json must include initial_storage_tb")
    overridden = {k for k in DEFAULTS if k in raw and raw[k] != DEFAULTS[k]}
    tags = {str(k): str(v).upper() for k, v in json.loads(Path(args.tags).read_text()).items()}
    months = expected_months(args.start, args.end)

    rows = load_csvs(args.csv)
    errors = validate(rows, months, tags)
    rows_per_month = dict(sorted(Counter(x["year_month"] for x in rows).items()))
    print("Rows per month:", json.dumps(rows_per_month))
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(2)
    print("Validation passed.")
    if args.validate_only:
        return

    r = calculate(rows, months, tags, inp)
    report = build_html(r, rows, months, tags, inp, overridden, date.today().isoformat())
    Path(args.out).write_text(report)
    print(f"Report: {args.out}")

    if args.results:
        res = {"utilization": r["util"], "avg_monthly_credits": r["avg_credits"],
               "starting_monthly_credits": r["starting_credits"], "month1_storage_tb": r["month1_tb"],
               "years": r["years"], "monthly": r["monthly"], "projection": r["projection"]}
        Path(args.results).write_text(json.dumps(res, indent=2))
        print(f"Results: {args.results}")

    for y in r["years"]:
        print(f"Year {y['year']}: {money(y['low'])} | {money(y['total'])} | {money(y['high'])}")


if __name__ == "__main__":
    main()
