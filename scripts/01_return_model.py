"""Return on Mentoring: a transparent cost-benefit model with uncertainty.

The question is framed as BREAK-EVEN: how large would a program's effect on high-school
graduation (and bachelor's completion) need to be for its lifetime benefits to cover its
cost? Effects and program costs are ILLUSTRATIVE ranges for the owner to replace with a real
program's budget and evaluated effects (Project 03); earnings come from BLS.

Per participant, in present value at program entry (age 16):
  annual earnings(level) = BLS median weekly earnings x 52 x (1 - unemployment rate)
  HS premium  = (HS diploma - no diploma) x causal share, ages 19-64
  BA premium  = (bachelor's - HS diploma) x causal share, ages 23-64,
                minus college costs (4 years of net price + forgone part of HS earnings, ages 19-22)
  benefits    = d_grad x PV(HS premium) + d_ba x PV(BA premium net of college costs)
  public share = tax rate x the earnings gains (taxes); participant share = the rest
  cost        = program cost per year x years
Run: python3 -I scripts/01_return_model.py -> output/ (params.json is read by the calculator)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

# ---------------- Data-based inputs ----------------
bls = pd.read_html(RAW / "bls_education_pays.html")[0]
bls.columns = ["level", "weekly", "unemp"]
bls = bls[pd.to_numeric(bls.weekly, errors="coerce").notna()].copy()
bls[["weekly", "unemp"]] = bls[["weekly", "unemp"]].astype(float)
B = bls.set_index("level")
annual = lambda lvl: B.loc[lvl, "weekly"] * 52 * (1 - B.loc[lvl, "unemp"] / 100)
E_LHS, E_HS, E_BA = annual("Less than a high school diploma"), annual("High school diploma"), annual("Bachelor's degree")
bridges = pd.read_csv(ROOT / "data" / "from_projects" / "bridge_colleges.csv")
np_q = bridges.net_price_low_income.quantile([0.25, 0.5, 0.75]).round(0).tolist()

# ---------------- Parameters (central, low, high; MC distribution) ----------------
P = {
    "earnings": {"less_than_hs": round(E_LHS), "hs_diploma": round(E_HS), "bachelors": round(E_BA),
                 "source": "BLS CPS annual averages (2025, 11-month), age 25+, full-time wage & salary median weekly x 52 x (1 - unemployment rate)"},
    "params": {
        "cost_per_year":  {"label": "Program cost per participant per year ($)", "central": 2000, "low": 1200, "high": 3500, "dist": "triangular", "basis": "Illustrative: replace with your program's budget"},
        "years":          {"label": "Years in program", "central": 1, "low": 1, "high": 2, "dist": "fixed", "basis": "Program design"},
        "d_grad":         {"label": "Effect on HS graduation (percentage points)", "central": 1.5, "low": 0.0, "high": 4.0, "dist": "triangular", "basis": "Illustrative: replace with evaluated effects (Project 03)"},
        "d_ba":           {"label": "Effect on bachelor's completion (percentage points)", "central": 0.5, "low": 0.0, "high": 2.0, "dist": "triangular", "basis": "Illustrative"},
        "causal_share":   {"label": "Share of the earnings gap caused by the degree", "central": 0.75, "low": 0.5, "high": 1.0, "dist": "uniform", "basis": "Raw gaps include selection; returns-to-schooling research supports most, not all"},
        "discount":       {"label": "Real discount rate", "central": 0.03, "low": 0.02, "high": 0.07, "dist": "fixed", "basis": "3% common for social programs; 7% conservative"},
        "growth":         {"label": "Real earnings growth per year", "central": 0.005, "low": 0.0, "high": 0.01, "dist": "uniform", "basis": "Assumption"},
        "tax_rate":       {"label": "Taxes as share of earnings gains", "central": 0.22, "low": 0.15, "high": 0.30, "dist": "uniform", "basis": "Federal + state + payroll; assumption"},
        "net_price":      {"label": "College net price per year, $0-30k families ($)", "central": np_q[1], "low": np_q[0], "high": np_q[2], "dist": "uniform", "basis": "Median and quartiles at Project 04 bridge colleges (College Scorecard)"},
        "forgone_share":  {"label": "Share of HS earnings forgone while in college", "central": 0.5, "low": 0.3, "high": 0.7, "dist": "fixed", "basis": "Many students work; assumption"},
    },
}


def pv(amount, start_age, end_age, r, g, entry=16):
    k = np.arange(start_age - entry, end_age - entry)
    return amount * np.sum(((1 + g) / (1 + r)) ** k)


def model(v):
    r, g, cs = v["discount"], v["growth"], v["causal_share"]
    hs_prem = pv((E_HS - E_LHS) * cs, 19, 65, r, g)
    ba_prem = pv((E_BA - E_HS) * cs, 23, 65, r, g)
    college = pv(v["net_price"] + v["forgone_share"] * E_HS, 19, 23, r, g)
    gain_earn = v["d_grad"] / 100 * hs_prem + v["d_ba"] / 100 * ba_prem
    benefits = gain_earn - v["d_ba"] / 100 * college
    cost = v["cost_per_year"] * v["years"]
    public = v["tax_rate"] * gain_earn
    return {"benefits": benefits, "cost": cost, "npv": benefits - cost, "bcr": benefits / cost,
            "public": public, "participant": benefits - public, "pv_hs_premium": hs_prem,
            "pv_ba_net": ba_prem - college, "breakeven_d_grad_pp": cost / hs_prem * 100}


central = {k: p["central"] for k, p in P["params"].items()}
C = model(central)

# ---------------- Monte Carlo ----------------
rng = np.random.default_rng(20261114)
N = 10000
draws = {}
for k, p in P["params"].items():
    if p["dist"] == "triangular":
        draws[k] = rng.triangular(p["low"], p["central"], p["high"], N)
    elif p["dist"] == "uniform":
        draws[k] = rng.uniform(p["low"], p["high"], N)
    else:
        draws[k] = np.full(N, p["central"], dtype=float)
mc = pd.DataFrame([model({k: draws[k][i] for k in draws}) for i in range(N)])
summ = mc[["benefits", "cost", "npv", "bcr", "public", "participant", "breakeven_d_grad_pp"]].describe(percentiles=[0.05, 0.5, 0.95]).T
summ["prob_positive_npv"] = np.nan
summ.loc["npv", "prob_positive_npv"] = (mc.npv > 0).mean()
summ.to_csv(OUT / "monte_carlo_summary.csv", float_format="%.3f")

# ---------------- Tornado (one at a time) ----------------
torn = []
for k, p in P["params"].items():
    if p["low"] == p["high"] or k == "tax_rate":  # tax rate only splits benefits; it never changes NPV
        continue
    lo = model({**central, k: p["low"]})["npv"]
    hi = model({**central, k: p["high"]})["npv"]
    torn.append({"param": k, "label": p["label"], "low_value": p["low"], "high_value": p["high"], "npv_at_low": lo, "npv_at_high": hi,
                 "swing": abs(hi - lo)})
torn = pd.DataFrame(torn).sort_values("swing", ascending=False)
torn.to_csv(OUT / "tornado.csv", index=False, float_format="%.0f")

# Break-even graduation effect across cost and discount rate
be = []
for cost in (1000, 1500, 2000, 2500, 3000, 4000, 5000):
    for r in (0.03, 0.07):
        be.append({"cost_per_participant": cost, "discount_rate": r,
                   "breakeven_d_grad_pp": model({**central, "cost_per_year": cost, "years": 1, "discount": r, "d_ba": 0})["breakeven_d_grad_pp"]})
be = pd.DataFrame(be)
be.to_csv(OUT / "breakeven_grid.csv", index=False, float_format="%.3f")

P["central_results"] = {k: round(float(v), 4) for k, v in C.items()}
P["monte_carlo"] = {"draws": N, "prob_positive_npv": round(float((mc.npv > 0).mean()), 4),
                    "bcr_p5": round(float(mc.bcr.quantile(0.05)), 3), "bcr_median": round(float(mc.bcr.median()), 3),
                    "bcr_p95": round(float(mc.bcr.quantile(0.95)), 3),
                    "public_share_of_benefits_median": round(float((mc.public / mc.benefits.where(mc.benefits > 0)).median()), 3)}
(OUT / "params.json").write_text(json.dumps(P, indent=2))

# ---------------- Figures ----------------
SURFACE, TEXT, TEXT2, GRID, C1, C2 = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#eb6834"
fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), dpi=100, gridspec_kw={"width_ratios": [1, 1.15]})
fig.patch.set_facecolor(SURFACE)
ax = axes[0]; ax.set_facecolor(SURFACE)
bins = np.linspace(0, min(mc.bcr.quantile(0.995), 40), 50)
ax.hist(mc.bcr.clip(upper=bins[-1]), bins=bins, color=C1, alpha=0.85)
ax.axvline(1, color=C2, lw=2)
ax.text(0.9, ax.get_ylim()[1] * 0.95, "break-even", color=C2, fontsize=10, ha="right")
ax.set_xlabel("Benefit-cost ratio (lifetime benefits per $1 of program cost)", color=TEXT2)
ax.set_ylabel("Simulations", color=TEXT2)
ax.set_title(f"Under the illustrative ranges, {(mc.npv > 0).mean():.0%} of {N:,} simulations break even", loc="left", color=TEXT, fontsize=12)
ax2 = axes[1]; ax2.set_facecolor(SURFACE)
t = torn.iloc[::-1]
y = np.arange(len(t))
base = C["npv"]
ax2.barh(y, t.npv_at_low - base, left=base, color=C2, height=0.6, label="Low end of range")
ax2.barh(y, t.npv_at_high - base, left=base, color=C1, height=0.6, label="High end of range")
ax2.axvline(0, color=TEXT2, lw=0.8)
ax2.axvline(base, color=TEXT, lw=1, ls="--")
ax2.set_yticks(y, t.label.str.replace("$", r"\$", regex=False), fontsize=9)  # escape $ (mathtext)
ax2.set_xlabel("Net present value per participant (\\$)", color=TEXT2)
ax2.set_title(f"What moves the answer most (central NPV \\${base:,.0f})", loc="left", color=TEXT, fontsize=12)
ax2.legend(frameon=False, labelcolor=TEXT, fontsize=9, loc="lower right")
for a_ in axes:
    a_.grid(axis="x", color=GRID, lw=0.6); a_.set_axisbelow(True)
    for s_ in ["top", "right"]:
        a_.spines[s_].set_visible(False)
    a_.tick_params(colors=TEXT2)
fig.text(0.02, 0.955, f"At \\$2,000 per participant, mentoring breaks even if it adds about {C['breakeven_d_grad_pp']:.0f} graduate per 100 participants",
         fontsize=13.5, weight="bold", color=TEXT)
fig.text(0.02, 0.012, "Earnings: BLS 2025 by education. Program costs and effects are illustrative ranges, not estimates for a real program. "
         "Verify before external use.", fontsize=8.5, color=TEXT2)
fig.subplots_adjust(left=0.06, right=0.98, top=0.86, bottom=0.14, wspace=0.66)
fig.savefig(OUT / "return_on_mentoring.png", dpi=150, facecolor=SURFACE)

pd.set_option("display.width", 200)
print({k: round(v) for k, v in {"E_LHS": E_LHS, "E_HS": E_HS, "E_BA": E_BA}.items()}, "net price q:", np_q)
print({k: round(v, 3) for k, v in C.items()})
print(P["monte_carlo"])
print(summ.round(2).to_string())
print(torn[["label", "npv_at_low", "npv_at_high"]].round(0).to_string(index=False))
print(be.pivot(index="cost_per_participant", columns="discount_rate", values="breakeven_d_grad_pp").round(2).to_string())
