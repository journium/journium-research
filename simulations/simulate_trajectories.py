"""
simulate_trajectories.py
========================
Empirical Monte Carlo verification of the absorbing Markov chain from
Section 5.1 of:

  "Behavioral Intelligence Platforms: From Event Streams to Autonomous Insight"
  Patra & Vadgave, 2026

This script samples trajectories from the published transition matrix in
markov_journey_model.py and confirms that, under the Markov property with a
common starting state, the empirical conditional conversion rate
P(converted | reached(s)) equals the closed-form absorption probability
B[s, converted]:

  P(converted | reached(s)) = B[s, converted]

This identity holds because, given that a journey has reached state s, the
strong Markov property makes the future evolution conditionally independent
of the past. The conditioning collapses the journey distribution to one
that effectively starts at s.

The script also reports:
  - Empirical reach rate (Eq. 11 of the paper)
  - Empirical P(converted | NOT reached(s))
  - Empirical lift (Eq. 12)
  - Empirical mean trajectory length (compare to row sum of N, Eq. 8)

These values reproduce Figure 3 (in its corrected form) and the fact bundle
in Section 7.2.

Usage
-----
    python simulate_trajectories.py
"""

from __future__ import annotations

import numpy as np

from markov_journey_model import (
    ABSORBING,
    B,
    N,
    P_full,
    TRANSIENT,
    n_t,
)

# ---------------------------------------------------------------------------
# Simulation parameters
# ---------------------------------------------------------------------------

N_TRIALS = 500_000
SEED = 42
START_STATE = TRANSIENT[0]  # sign_up

# ---------------------------------------------------------------------------
# Run Monte Carlo
# ---------------------------------------------------------------------------


def simulate() -> dict:
    """Sample N_TRIALS journeys from START_STATE and collect statistics."""
    states = TRANSIENT + ABSORBING
    idx = {s: i for i, s in enumerate(states)}
    absorbing_idx = {idx[a] for a in ABSORBING}
    converted_idx = idx["converted"]
    start_idx = idx[START_STATE]
    n_states = len(states)

    rng = np.random.default_rng(SEED)

    visit_counts = {s: 0 for s in TRANSIENT}
    visit_and_converted = {s: 0 for s in TRANSIENT}
    not_visit_and_converted = {s: 0 for s in TRANSIENT}
    total_converted = 0
    total_steps = 0

    for _ in range(N_TRIALS):
        cur = start_idx
        visited: set[int] = set()
        steps = 0
        while cur not in absorbing_idx:
            visited.add(cur)
            cur = rng.choice(n_states, p=P_full[cur])
            steps += 1
        total_steps += steps
        converted = cur == converted_idx
        if converted:
            total_converted += 1
        for v_idx in range(n_t):
            s = TRANSIENT[v_idx]
            if v_idx in visited:
                visit_counts[s] += 1
                if converted:
                    visit_and_converted[s] += 1
            else:
                if converted:
                    not_visit_and_converted[s] += 1

    return {
        "total_converted": total_converted,
        "total_steps": total_steps,
        "visit_counts": visit_counts,
        "visit_and_converted": visit_and_converted,
        "not_visit_and_converted": not_visit_and_converted,
    }


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 72)
    print("Trajectory Simulation — BIP Empirical Verification")
    print("=" * 72)
    print(f"\nStart state          : {START_STATE}")
    print(f"Trajectories sampled : {N_TRIALS:,}")
    print(f"Random seed          : {SEED}")

    stats = simulate()
    overall_conv = stats["total_converted"] / N_TRIALS
    mean_steps = stats["total_steps"] / N_TRIALS

    t_start = N.sum(axis=1)[TRANSIENT.index(START_STATE)]
    print(f"\nOverall conversion rate         : {overall_conv:.4f}")
    print(f"  (formal: B[{START_STATE}, converted] = {B[TRANSIENT.index(START_STATE), 0]:.4f})")
    print(f"Mean trajectory length          : {mean_steps:.4f}")
    print(f"  (formal: t[{START_STATE}] = sum_j N[{START_STATE},j] = {t_start:.4f})")

    print("\n--- Per-state empirical conditionals ---")
    print(
        f"  {'state':<22} {'reach':>8} {'P(c|r)':>10} {'B[s,c]':>10} "
        f"{'P(c|!r)':>10} {'lift':>8}"
    )
    print("  " + "-" * 70)
    for s_idx, s in enumerate(TRANSIENT):
        n_reached = stats["visit_counts"][s]
        n_not_reached = N_TRIALS - n_reached
        reach = n_reached / N_TRIALS
        p_conv_reached = (
            stats["visit_and_converted"][s] / n_reached if n_reached > 0 else float("nan")
        )
        if n_not_reached > 0:
            p_conv_not_reached = stats["not_visit_and_converted"][s] / n_not_reached
        else:
            p_conv_not_reached = float("nan")

        if (
            not np.isnan(p_conv_not_reached)
            and p_conv_not_reached > 0
            and not np.isnan(p_conv_reached)
        ):
            lift_val = p_conv_reached / p_conv_not_reached
            lift_str = f"{lift_val:>8.3f}"
        else:
            lift_str = f"{'undef':>8s}"

        nr_str = (
            f"{p_conv_not_reached:>10.4f}"
            if not np.isnan(p_conv_not_reached)
            else f"{'undef':>10s}"
        )

        print(
            f"  {s:<22} {reach:>8.4f} {p_conv_reached:>10.4f} "
            f"{B[s_idx, 0]:>10.4f} {nr_str} {lift_str}"
        )

    print(
        "\n  Note: P(c|r) and B[s,c] should agree to within sampling noise."
        "\n  This is the Markov-property identity from Section 5.1.2 (corrected)."
    )

    # ------------------------------------------------------------------
    # Reproduce Figure 3 corrected values (B[s, converted])
    # ------------------------------------------------------------------
    print("\n--- Values reproducing Figure 3 (formal absorption probabilities) ---")
    print(f"  {'state':<22} {'B[s, converted]':>16}")
    for s_idx, s in enumerate(TRANSIENT):
        print(f"  {s:<22} {B[s_idx, 0]:>16.4f}")

    # ------------------------------------------------------------------
    # Reproduce Section 7.2 fact bundle (corrected) for import_data
    # ------------------------------------------------------------------
    print("\n--- Section 7.2 fact bundle reproduction (state = import_data) ---")
    s = "import_data"
    s_idx = TRANSIENT.index(s)
    n_reached = stats["visit_counts"][s]
    n_not_reached = N_TRIALS - n_reached
    reach = n_reached / N_TRIALS
    p_conv_reached = stats["visit_and_converted"][s] / n_reached
    p_conv_not_reached = stats["not_visit_and_converted"][s] / n_not_reached
    lift_val = p_conv_reached / p_conv_not_reached
    print(f"  reach_rate                    : {reach:.4f}")
    print(f"  P(converted | reached)        : {p_conv_reached:.4f}")
    print(f"  P(converted | not reached)    : {p_conv_not_reached:.4f}")
    print(f"  lift                          : {lift_val:.4f}")
    print(
        f"  transitions_to invite_teammate: "
        f"{P_full[TRANSIENT.index('import_data'), TRANSIENT.index('invite_teammate')]:.4f}"
    )
    print(
        f"  is_dropoff_point_for dropped_off (P_dropoff): "
        f"{P_full[TRANSIENT.index('import_data'), n_t + ABSORBING.index('dropped_off')]:.4f}"
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
