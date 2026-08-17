# Policy Sensitivity Analysis — Reproducible Notebook Equivalent

> Local simulator experiment only. This is not interoperability, public transport,
> an uncounted warm-up, or a counted league operation.

## Question and preregistered design

How do existing board-size and survival-threshold parameters affect capture outcomes for the frozen champion and a direct scent baseline against two existing observation-only Thief policies?

The run uses 2,400 games: 40 paired seeds, three start scenarios,
four existing policy pairings, and five one-factor-at-a-time (OAT) settings. All other
GameConfig fields remain fixed. ScentTacticalPolice remains frozen; no policy was trained
or changed.

## Estimands and equations

Capture rate is $\hat{p}=c/n$. Uncertainty uses the Wilson 95% score interval:

$$\frac{\hat p + z^2/(2n) \pm z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n},\quad z=1.95996.$$

The paired OAT elementary effect for factor $i$ is

$$\Delta_i = \frac{\hat p(x_i')-\hat p(x_i)}{x_i'-x_i}.$$

## Aggregate results

| Setting | Police | Thief | Games | Capture | Wilson 95% | Police score | Thief score |
|---|---|---|---:|---:|---:|---:|---:|
| board_7_survival_35 | ScentTacticalPolice | BarrierAwareThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_35 | ScentTacticalPolice | ScentEvasionThief | 120 | 84.2% | [76.6%, 89.6%] | 17.62 | 5.79 |
| board_7_survival_35 | ScentGreedyPolice | BarrierAwareThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_35 | ScentGreedyPolice | ScentEvasionThief | 120 | 76.7% | [68.3%, 83.3%] | 16.50 | 6.17 |
| board_9_survival_35 | ScentTacticalPolice | BarrierAwareThief | 120 | 98.3% | [94.1%, 99.5%] | 19.75 | 5.08 |
| board_9_survival_35 | ScentTacticalPolice | ScentEvasionThief | 120 | 73.3% | [64.8%, 80.4%] | 16.00 | 6.33 |
| board_9_survival_35 | ScentGreedyPolice | BarrierAwareThief | 120 | 99.2% | [95.4%, 99.9%] | 19.88 | 5.04 |
| board_9_survival_35 | ScentGreedyPolice | ScentEvasionThief | 120 | 73.3% | [64.8%, 80.4%] | 16.00 | 6.33 |
| board_11_survival_35 | ScentTacticalPolice | BarrierAwareThief | 120 | 82.5% | [74.7%, 88.3%] | 17.38 | 5.88 |
| board_11_survival_35 | ScentTacticalPolice | ScentEvasionThief | 120 | 60.8% | [51.9%, 69.1%] | 14.12 | 6.96 |
| board_11_survival_35 | ScentGreedyPolice | BarrierAwareThief | 120 | 98.3% | [94.1%, 99.5%] | 19.75 | 5.08 |
| board_11_survival_35 | ScentGreedyPolice | ScentEvasionThief | 120 | 65.8% | [57.0%, 73.7%] | 14.88 | 6.71 |
| board_7_survival_50 | ScentTacticalPolice | BarrierAwareThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_50 | ScentTacticalPolice | ScentEvasionThief | 120 | 97.5% | [92.9%, 99.1%] | 19.62 | 5.12 |
| board_7_survival_50 | ScentGreedyPolice | BarrierAwareThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_50 | ScentGreedyPolice | ScentEvasionThief | 120 | 89.2% | [82.3%, 93.6%] | 18.38 | 5.54 |
| board_7_survival_70 | ScentTacticalPolice | BarrierAwareThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_70 | ScentTacticalPolice | ScentEvasionThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_70 | ScentGreedyPolice | BarrierAwareThief | 120 | 100.0% | [96.9%, 100.0%] | 20.00 | 5.00 |
| board_7_survival_70 | ScentGreedyPolice | ScentEvasionThief | 120 | 94.2% | [88.4%, 97.1%] | 19.12 | 5.29 |

## Paired elementary effects

| Setting | Pairing | Capture delta | Effect per unit |
|---|---|---:|---:|
| board_9_survival_35 | ScentTacticalPolice vs BarrierAwareThief | -1.7% | -0.00833 |
| board_9_survival_35 | ScentTacticalPolice vs ScentEvasionThief | -10.8% | -0.05417 |
| board_9_survival_35 | ScentGreedyPolice vs BarrierAwareThief | -0.8% | -0.00417 |
| board_9_survival_35 | ScentGreedyPolice vs ScentEvasionThief | -3.3% | -0.01667 |
| board_11_survival_35 | ScentTacticalPolice vs BarrierAwareThief | -17.5% | -0.04375 |
| board_11_survival_35 | ScentTacticalPolice vs ScentEvasionThief | -23.3% | -0.05833 |
| board_11_survival_35 | ScentGreedyPolice vs BarrierAwareThief | -1.7% | -0.00417 |
| board_11_survival_35 | ScentGreedyPolice vs ScentEvasionThief | -10.8% | -0.02708 |
| board_7_survival_50 | ScentTacticalPolice vs BarrierAwareThief | +0.0% | +0.00000 |
| board_7_survival_50 | ScentTacticalPolice vs ScentEvasionThief | +13.3% | +0.00889 |
| board_7_survival_50 | ScentGreedyPolice vs BarrierAwareThief | +0.0% | +0.00000 |
| board_7_survival_50 | ScentGreedyPolice vs ScentEvasionThief | +12.5% | +0.00833 |
| board_7_survival_70 | ScentTacticalPolice vs BarrierAwareThief | +0.0% | +0.00000 |
| board_7_survival_70 | ScentTacticalPolice vs ScentEvasionThief | +15.8% | +0.00452 |
| board_7_survival_70 | ScentGreedyPolice vs BarrierAwareThief | +0.0% | +0.00000 |
| board_7_survival_70 | ScentGreedyPolice vs ScentEvasionThief | +17.5% | +0.00500 |

## Interpretation

The frozen champion baseline spans 84.2% to 100.0% across the two Thief policies after pooling scenarios.
The largest observed paired shift is -23.3% for ScentTacticalPolice vs ScentEvasionThief at board_11_survival_35.
These are measured associations inside the declared simulator grid, not a new competitive
policy decision and not evidence about another team's implementation.

## Limitations and threats to validity

- OAT is a screening design and cannot estimate factor interactions; this is not a Sobol
  or other global variance-based sensitivity analysis.
- Forty deterministic seeds and three starts support paired comparison but do not
  make the
  confidence interval a guarantee for unseen terrains, teams, or implementations.
- The simulator exposes evaluator outcomes only after actions; policies still receive
  Observation-only inputs. No objective opponent coordinate is published.
- Timing is deliberately excluded from deterministic artifacts and remains under
  COST-001.

## References

- Morris (1991), OAT elementary effects: https://doi.org/10.1080/00401706.1991.10484804
- Saltelli et al. (2010), variance-based global sensitivity and interaction limits:
  https://doi.org/10.1016/j.cpc.2009.09.018
- Wilson (1927), binomial score interval:
  https://doi.org/10.1080/01621459.1927.10502953

## Reproduction

```bash
uv run python -m tools.research.cli
```

The command performs only local simulator experiments and overwrites only the six curated
publication files listed in the manifest.
