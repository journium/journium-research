"""
interestingness_scoring.py
==========================
Demonstrates the composite interestingness scoring framework from Section 5.5 of:

  "Behavioral Intelligence Platforms: From Event Streams to Autonomous Insight"
  Patra & Vadgave, 2026

The composite score is defined as (Eq. 9):

  score(f) = alpha * significance
           + beta  * magnitude
           + gamma * reach
           + omega * actionability
           + eps   * novelty

where all component scores are normalised to [0, 1].

This script generates a synthetic set of detector findings, scores each one,
ranks them, and prints the prioritised insight feed.

Usage
-----
    python interestingness_scoring.py
"""

import numpy as np


# ---------------------------------------------------------------------------
# Weight configuration (configurable per monitoring context)
# ---------------------------------------------------------------------------

WEIGHTS = {
    "alpha": 0.30,   # statistical significance (1 - p-value, penalised for small N)
    "beta":  0.25,   # effect magnitude (normalised)
    "gamma": 0.20,   # population reach fraction
    "omega": 0.15,   # actionability heuristic
    "eps":   0.10,   # novelty (recency relative to prior snapshots)
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1"


# ---------------------------------------------------------------------------
# Synthetic findings
# Each finding is a dict with raw metric values; scoring normalises them.
# ---------------------------------------------------------------------------

FINDINGS = [
    {
        "id": "F001",
        "description": "email_verified → profile_complete drop-off increased 18 pp after v2.3 release",
        "detector": "TemporalRegressionDetector",
        "p_value": 0.003,
        "sample_size": 2_400,
        "effect_size": 0.18,    # |ΔP| / P_{t-1}
        "reach": 0.71,          # fraction of user population affected
        "actionable": True,
        "snapshots_since_first_seen": 1,
    },
    {
        "id": "F002",
        "description": "feature_used is activation driver for 'converted' (lift = 4.2x)",
        "detector": "ActivationDriverDetector",
        "p_value": 0.001,
        "sample_size": 1_800,
        "effect_size": 3.20,    # |lift - 1| normalised to [0,1] below
        "reach": 0.45,
        "actionable": True,
        "snapshots_since_first_seen": 3,
    },
    {
        "id": "F003",
        "description": "Unexpected loop detected: profile_complete → sign_up (8% of users)",
        "detector": "UnexpectedLoopDetector",
        "p_value": 0.04,
        "sample_size": 310,
        "effect_size": 0.08,
        "reach": 0.08,
        "actionable": False,
        "snapshots_since_first_seen": 2,
    },
    {
        "id": "F004",
        "description": "Mobile segment conversion rate 22 pp below desktop (segment divergence)",
        "detector": "SegmentDivergenceDetector",
        "p_value": 0.008,
        "sample_size": 950,
        "effect_size": 0.22,
        "reach": 0.38,
        "actionable": True,
        "snapshots_since_first_seen": 5,
    },
    {
        "id": "F005",
        "description": "Drop-off cluster at sign_up → abandoned (low significance, small N)",
        "detector": "DropOffClusterDetector",
        "p_value": 0.12,
        "sample_size": 85,
        "effect_size": 0.11,
        "reach": 0.05,
        "actionable": False,
        "snapshots_since_first_seen": 7,
    },
]


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

MIN_SAMPLE = 100  # n_min for sample-size penalty in significance score


def score_significance(p_value: float, sample_size: int) -> float:
    """
    Statistical confidence penalised for small sample sizes.
    significance = (1 - p_value) * min(1, log(n / n_min) / log(10))
    Clipped to [0, 1].
    """
    base = 1.0 - p_value
    penalty = min(1.0, np.log(max(sample_size, 1) / MIN_SAMPLE) / np.log(10))
    return float(np.clip(base * penalty, 0.0, 1.0))


def score_magnitude(effect_size: float) -> float:
    """Normalise effect size to [0, 1] using a soft cap at 1.0."""
    return float(np.clip(effect_size, 0.0, 1.0))


def score_novelty(snapshots_since_first_seen: int) -> float:
    """Decay novelty exponentially; novel findings (snapshot 1) score 1.0."""
    return float(np.exp(-0.3 * (snapshots_since_first_seen - 1)))


def composite_score(finding: dict) -> float:
    sig  = score_significance(finding["p_value"], finding["sample_size"])
    mag  = score_magnitude(finding["effect_size"])
    reach = float(np.clip(finding["reach"], 0.0, 1.0))
    action = 1.0 if finding["actionable"] else 0.0
    nov  = score_novelty(finding["snapshots_since_first_seen"])

    return (
        WEIGHTS["alpha"] * sig
        + WEIGHTS["beta"]  * mag
        + WEIGHTS["gamma"] * reach
        + WEIGHTS["omega"] * action
        + WEIGHTS["eps"]   * nov
    )


# ---------------------------------------------------------------------------
# Score and rank
# ---------------------------------------------------------------------------

def main() -> None:
    scored = []
    for f in FINDINGS:
        s = composite_score(f)
        scored.append({**f, "score": s})

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)

    print("=" * 72)
    print("Composite Interestingness Score — BIP Insight Prioritisation Demo")
    print("=" * 72)
    print(f"\nWeights: {WEIGHTS}\n")

    print(f"{'Rank':<5} {'ID':<6} {'Score':>6}  {'Description'}")
    print("-" * 72)
    for rank, f in enumerate(ranked, start=1):
        print(f"  {rank:<3} {f['id']:<6} {f['score']:.4f}  {f['description']}")

    print("\n--- Component breakdown (top finding) ---")
    top = ranked[0]
    sig  = score_significance(top["p_value"], top["sample_size"])
    mag  = score_magnitude(top["effect_size"])
    reach = float(np.clip(top["reach"], 0.0, 1.0))
    action = 1.0 if top["actionable"] else 0.0
    nov  = score_novelty(top["snapshots_since_first_seen"])
    print(f"  Finding    : {top['id']} — {top['description']}")
    print(f"  Significance (alpha={WEIGHTS['alpha']}): {sig:.4f}  contribution={WEIGHTS['alpha']*sig:.4f}")
    print(f"  Magnitude   (beta ={WEIGHTS['beta']} ): {mag:.4f}  contribution={WEIGHTS['beta']*mag:.4f}")
    print(f"  Reach       (gamma={WEIGHTS['gamma']}): {reach:.4f}  contribution={WEIGHTS['gamma']*reach:.4f}")
    print(f"  Actionable  (omega={WEIGHTS['omega']}): {action:.4f}  contribution={WEIGHTS['omega']*action:.4f}")
    print(f"  Novelty     (eps  ={WEIGHTS['eps']}  ): {nov:.4f}  contribution={WEIGHTS['eps']*nov:.4f}")
    print(f"  Total score : {top['score']:.4f}")
    print("=" * 72)


if __name__ == "__main__":
    main()
