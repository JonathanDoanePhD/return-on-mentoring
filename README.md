# 07 - Return on Mentoring

**Question:** What would a mentoring program have to achieve for its lifetime benefits to
cover its cost? This is the economic side of Project 03 (Impact Engine), in the spirit of a
social-return reporting dashboard: costs, $1 invested → $X returned, net present value, and
who receives the benefits.

**Status:** complete (2026-11-14). The interactive calculator is ready to use with a real
program's budget and evaluated effects.

> **Illustrative, not an estimate for any real program.** Program costs and effects are
> placeholder ranges. Earnings come from BLS. Check every figure against original sources
> before funder use, and replace the placeholders with your program's numbers.

## Key findings

**Inputs from data:** BLS 2025 (11-month averages; October missing because of the federal
shutdown), age 25+, full-time median weekly earnings adjusted for unemployment:
**$37,598** a year without a diploma, **$48,072** with a high school diploma, **$79,758**
with a bachelor's degree. College net price for families earning $0-30k: median **$8,474**
(Project 04 bridge colleges).

1. **Break-even is about one extra graduate per 100 participants.** At $2,000 per
   participant and a 3% discount rate, a program pays back its cost if it raises high school
   graduation by **~1.0 percentage point** (2.0 at a 7% discount rate). That's an extra 1 in
   100 participants; or, where about 14% of disadvantaged students don't graduate (Project
   02's high schools average ~86%), turning about 1 in 14 likely non-graduates into
   graduates.
2. **Each extra graduate is worth about $204,000** in lifetime earnings, in today's dollars
   at 3%, counting only 75% of the raw earnings gap as caused by the diploma.
3. **Break-even scales with cost:** about 0.5 points at $1,000 per participant, 1.5 at
   $3,000 and 2.5 at $5,000 (3% discount; double these at 7%).
4. **The effect sizes matter far more than anything else.** Holding the rest at central
   values, the graduation and bachelor's effects swing net value most, followed by the
   discount rate and the causal share of the earnings gap. College price and forgone
   earnings barely matter. So the evaluation (Project 03) matters more than refining the
   economics.
5. **About a quarter of benefits go to the public** (median 25%, as taxes on higher
   earnings); the rest go to participants.
6. **Under the illustrative ranges,** 98% of 10,000 simulations break even (benefit per $1:
   1.28 at the 5th percentile, 6.43 at the 95th). That only restates the assumed effects,
   which include no negative effects. The useful output is the break-even threshold, not the
   probability.

**Connecting to Project 03:** the Impact Engine expects *measured* effects of about
0.07-0.16 SD on engagement and belonging. How those translate into graduation points is not
known from public data. The most decision-relevant next step for a real program is to link
participants to graduation records, with consent and a data-sharing agreement, so the
calculator can use a measured graduation effect.

## Outputs

| File | What |
|---|---|
| `output/calculator.html` | Interactive calculator: sliders for every assumption, results board, break-even line, benefit split, 2,000-draw simulation (`calculator_fragment.html` = same page without html/head wrapper) |
| `output/params.json` | All assumptions (with basis), BLS-derived earnings, central and Monte Carlo results (read by the calculator) |
| `output/monte_carlo_summary.csv` | 10,000-draw summary: benefits, cost, NPV, benefit-cost ratio, public/participant split |
| `output/tornado.csv` | One-at-a-time sensitivity |
| `output/breakeven_grid.csv` | Break-even graduation effect by cost per participant and discount rate |
| `output/return_on_mentoring.png` | Figure: distribution of benefit-cost ratios + sensitivity |

## Rebuild

```bash
python3 -I scripts/fetch_data.py .
python3 -I scripts/01_return_model.py      # model, Monte Carlo, params.json
python3 -I scripts/02_build_calculator.py  # calculator page
```

`data/from_projects/bridge_colleges.csv` comes from Project 04. The calculator's JavaScript
uses the same formula as the Python model; the page's central result was checked to match
it ($3,124 net value; $2.56 per $1).

## Model

Present value at program entry (age 16):
- annual earnings by level = BLS weekly × 52 × (1 − unemployment rate)
- extra HS graduate: (HS − no diploma) × causal share, ages 19-64
- extra bachelor's completer: (BA − HS) × causal share, ages 23-64, minus four years of
  net price and the forgone share of HS earnings at ages 19-22
- benefits = Δgraduation × PV(HS premium) + Δbachelor's × PV(BA premium − college costs)
- public share = tax rate × earnings gains; participant share = the remainder
- cost = cost per year × years

| Assumption | Central | Range | Basis |
|---|---|---|---|
| Cost per participant per year | $2,000 | $1,200-3,500 | Illustrative |
| HS graduation effect | 1.5 pts | 0-4 | Illustrative |
| Bachelor's effect | 0.5 pts | 0-2 | Illustrative |
| Causal share of earnings gap | 75% | 50-100% | Returns-to-schooling research (verify) |
| Real discount rate | 3% | 2-7% | Common for social programs |
| Real earnings growth | 0.5% | 0-1% | Assumption |
| Taxes on earnings gains | 22% | 15-30% | Assumption |
| College net price ($0-30k) | $8,474 | $5,423-10,536 | Project 04 bridge colleges |
| Forgone HS earnings in college | 50% | 30-70% | Assumption |

## Caveats

- Earnings only. Leaves out health, civic, family and public-spending benefits, so the
  estimate is narrow (conservative in that sense), but it also ignores possible negative
  effects.
- BLS medians cover full-time workers. Differences in labor force participation by education
  are not captured beyond unemployment.
- 2025 BLS figures are 11-month averages and not strictly comparable with other years.

## Cross-check with Project 08 (2026-11-19)

Project 08's evidence map of 935 ERIC mentoring studies supports keeping the graduation
effect at **1.5 points (range 0-4)**. Weak designs report large graduation gains (median 15-35
points), but the only randomized percentage-point estimate is from college coaching (4-15
points, median 5). The K-12 randomized trials are mostly null (3 null, 1 positive, 1 mixed).
The break-even of about 1 point is plausible but not established. See
`https://github.com/JonathanDoanePhD/mentoring-evidence-engine/blob/main/output/priors.json`. The figures come from abstracts and need
verification.

## License, citation and data terms

- **Code:** MIT (proposed; see `LICENSE`). **Outputs:** CC BY 4.0 (proposed), subject to the source terms below.
- **Cite this project as:** JonathanDoanePhD (2026). *Return on Mentoring*. https://github.com/JonathanDoanePhD/return-on-mentoring
- **Data sources and terms** (from `data/sources.csv`; recorded versions and checksums in `data/sources.lock.csv`):

| Source | Terms |
|---|---|
| BLS Employment Projections: earnings and unemployment by educational attainment (CPS annual averages) | U.S. government work (public domain) |

Built with AI assistance (Claude). Exploratory research: every statistic needs checking against its original source
before it appears in funder reports, grant applications or public material.

## Before public release

- [ ] Every statistic in this README and in `output/` is checked against its original source.
- [ ] Replace the illustrative costs and effects with a real program's before using results.
- [ ] bls.gov blocked downloads from the development environment; confirm the BLS table still downloads.
- [ ] The owner confirms the license choice above.
