# Baseline Experiments

## Purpose

This baseline provides reproducible first-match observations for the pure causal-entropy strategy against the three
conventional computer strategies and against itself. It is a reference dataset, not a statistical performance claim.

## Reproducibility Contract

| Item | Value |
|---|---|
| Measurement date | June 15, 2026 |
| Python | 3.12.10 |
| Platform | Windows x64 |
| Causal horizon | 5 |
| Temperature | 1.0 |
| Causal tie-breaker | Seeded random |
| Tactical/minimax tie-breaker | Deterministic |
| Timing | Median of five isolated application processes |
| Software revision | `sha256:b9cf9a5c...39bc86c9` |

The full revision digest is
`b9cf9a5c621c5c641bee13b7a68d62d54250b7d8509050fd473ac11b39bc86c9`. It covers the launchers, runtime modules,
runtime requirements, and canonical experiment configurations. The integration test recalculates it and fails if
any experiment input changes without a deliberate baseline update. Text newlines are normalized before hashing so
the revision remains stable across Windows, Linux, and Git archive checkouts.

## Results

| Configuration | Seed | Result | Moves | Action sequence | Median |
|---|---:|---|---:|---|---:|
| Causal vs causal | 8401 | Draw | 9 | `b1 b3 a3 a1 a2 b2 c3 c2 c1` | 494.634 ms |
| Causal vs minimax | 8301 | Draw | 9 | `a2 a1 b1 b2 c3 c1 a3 b3 c2` | 492.907 ms |
| Causal vs random | 8101 | O wins | 8 | `c2 c1 b1 a3 c3 a1 b3 a2` | 445.014 ms |
| Causal vs tactical | 8201 | Draw | 9 | `a2 b2 b1 a1 c3 c1 a3 b3 c2` | 444.498 ms |
| Minimax vs causal | 8302 | X wins | 7 | `a1 a2 b1 c1 b2 c3 b3` | 565.777 ms |
| Random vs causal | 8102 | Draw | 9 | `c3 c2 b3 a3 b1 b2 c1 a1 a2` | 249.188 ms |
| Tactical vs causal | 8202 | X wins | 7 | `b2 b3 a1 c3 a3 a2 c1` | 248.019 ms |

Player 1 is `X`; Player 2 is `O`. Complete selected-move diagnostics are summarized below.

## Causal Diagnostics

The table shows the selected causal action at each causal turn. Each entry is
`move:action score [current paths -> successor paths]`.

| Configuration | Selected causal diagnostics |
|---|---|
| Causal vs causal | `1:b1 -0.865990 [15120->6360]`; `2:b3 -1.000733 [6360->2338]`; `3:a3 -1.283160 [2338->648]`; `4:a1 -1.737692 [648->114]`; `5:a2 -1.558145 [114->24]`; `6:b2 -1.386294 [24->6]`; `7:c3 -1.098612 [6->2]`; `8:c2 -0.693147 [2->1]`; `9:c1 0.000000 [1->1]` |
| Causal vs minimax | `1:a2 -0.865990 [15120->6360]`; `3:b1 -1.273345 [2258->632]`; `5:c3 -1.427116 [100->24]`; `7:a3 -1.098612 [6->2]`; `9:c2 0.000000 [1->1]` |
| Causal vs random | `1:c2 -0.865990 [15120->6360]`; `3:b1 -1.273345 [2258->632]`; `5:c3 -1.532898 [88->19]`; `7:b3 -1.098612 [6->2]` |
| Causal vs tactical | `1:a2 -0.865990 [15120->6360]`; `3:b1 -1.302656 [2178->592]`; `5:c3 -1.427116 [100->24]`; `7:a3 -1.098612 [6->2]`; `9:c2 0.000000 [1->1]` |
| Minimax vs causal | `2:a2 -1.020214 [6180->2228]`; `4:c1 -1.476964 [473->108]`; `6:c3 -1.280934 [18->5]` |
| Random vs causal | `2:c2 -1.020214 [6180->2228]`; `4:a3 -1.476964 [473->108]`; `6:b2 -1.252763 [21->6]`; `8:a1 -0.693147 [2->1]` |
| Tactical vs causal | `2:b3 -1.041287 [6000->2118]`; `4:c3 -1.651060 [417->80]`; `6:a2 -1.280934 [18->5]` |

Scores are the configured temperature multiplied by the natural-log entropy difference:

$$
C(s,a) = T \left[\log |\Gamma_\tau(s_a)| - \log |\Gamma_\tau(s)|\right]
$$

## Reproduction

Run one canonical match:

```text
python main.py config/experiments/causal-entropy-x-minimax-o.yaml
```

Every canonical configuration enables computer score tables. The terminal output therefore exposes all candidate
scores, including the selected score and exact path counts for every causal turn.

## Interpretation And Limitations

- Seven single games cannot estimate win rates or statistical significance.
- Seeds make these exact matches repeatable; they do not make them representative.
- Both players share one seeded random generator, so player order changes the sequence of random values consumed.
- Timing includes interpreter startup, configuration loading, search, rendering, and process shutdown.
- Timing varies by hardware, operating system, Python build, and machine load.
- The pure causal strategy values future option count only. It may ignore an immediate win or permit a loss.
- Minimax models adversarial optimal play; causal entropy counts all legal futures uniformly. Their objectives differ.
- Tic-tac-toe is finite and small enough for exhaustive search. Results should not be generalized to larger domains.
- No result here supports a claim that causal entropy is a complete or superior theory of intelligence.
