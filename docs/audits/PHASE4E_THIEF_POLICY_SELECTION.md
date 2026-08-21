# Phase 4E — Thief Policy Selection

Classification: **offline local-simulator experiment**. No opponent, no network, no counted play.

## Why

The peer runtime hard-coded `RandomLegalThief`, an integration default chosen to debug the
protocol rather than to score. The 2026-08-21 uncounted warm-up made the cost visible: our thief
was cornered on step 15 while our frozen police won its own game in 10. In a six-sub-game series a
team plays thief three times, and the official table pays a thief 5 for a capture and 10 for
surviving, so the policy is worth up to 15 points per series.

## Method

Every pairing ran on the exact negotiated match configuration loaded from
`interop/fixtures/phase4a5_reference_profile.json` — 7x7, police `[0,0]`, thief `[3,3]`, barrier
quota 14, survival threshold 35 — not on the Phase 2.5 scenario set. Seeds 1 through 200 per
pairing, 3000 games total, 112.3 s, through the existing `run_batch` harness. Policies received
only role-legal observations; no policy reads a hidden opponent position.

The three police columns are our frozen policy, a plain scent chaser as the shape most opponents
implement, and a random police as the weak-opponent bound.

## Measured

| Police | Thief | Thief survival | Mean thief points | Mean thief actions |
|---|---|---:|---:|---:|
| ScentTacticalPolice (ours, frozen) | RandomLegalThief (current default) | 0.5% | 5.03 | 8.0 |
| ScentTacticalPolice (ours, frozen) | SpaceSeekingThief | 0.0% | 5.0 | 6.0 |
| ScentTacticalPolice (ours, frozen) | BarrierAwareThief | 0.0% | 5.0 | 8.3 |
| ScentTacticalPolice (ours, frozen) | ScentEvasionThief | 14.5% | 5.72 | 19.3 |
| ScentTacticalPolice (ours, frozen) | LookaheadEvasionThief | 80.0% | 9.0 | 32.2 |
| ScentGreedyPolice (typical opponent shape) | RandomLegalThief (current default) | 0.0% | 5.0 | 7.1 |
| ScentGreedyPolice (typical opponent shape) | SpaceSeekingThief | 0.0% | 5.0 | 6.0 |
| ScentGreedyPolice (typical opponent shape) | BarrierAwareThief | 0.0% | 5.0 | 8.9 |
| ScentGreedyPolice (typical opponent shape) | ScentEvasionThief | 21.0% | 6.05 | 19.8 |
| ScentGreedyPolice (typical opponent shape) | LookaheadEvasionThief | 100.0% | 10.0 | 35.0 |
| RandomLegalPolice (weak opponent shape) | RandomLegalThief (current default) | 93.0% | 9.65 | 33.2 |
| RandomLegalPolice (weak opponent shape) | SpaceSeekingThief | 94.0% | 9.7 | 34.0 |
| RandomLegalPolice (weak opponent shape) | BarrierAwareThief | 99.5% | 9.97 | 34.9 |
| RandomLegalPolice (weak opponent shape) | ScentEvasionThief | 100.0% | 10.0 | 35.0 |
| RandomLegalPolice (weak opponent shape) | LookaheadEvasionThief | 100.0% | 10.0 | 35.0 |

## Reading

Against a plain scent chaser — the shape the one real opponent we have played resembles — the
current default survives **0%** of games and `LookaheadEvasionThief` survives **100%**. Against our
own strongest police the same swap moves survival from 0.5% to 80%, and mean thief points from
5.03 to 9.00. `ScentEvasionThief`, the Phase 2.5 champion, is clearly better than the default and
clearly worse than `LookaheadEvasionThief` on this configuration.

## Honest limits

Every number above is measured against **our own** police policies. No opponent's police is
modelled here, and a stronger real police could compress these margins. The experiment says which
thief is better on this board against these pursuit shapes; it does not predict a league placing.

## What changed in the code

`peer_cli` gained `--thief-policy`, resolved through `interop/runtime_policies.py`. The **default
is deliberately unchanged**: without the flag the runtime still builds `RandomLegalThief`, so the
published thief role repository README stays accurate and no silent competitive change occurs.
The Police policy remains frozen and is not selectable; supplying `--thief-policy` for the police
role is refused rather than ignored.

Adopting a different default is a separate decision. It requires updating the role repository
README and the policy-status label, and republishing the role repositories.
