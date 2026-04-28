"""
removal_effect.py
=================
Demonstrates the removal effect computation from Section 5.4 of:

  "Behavioral Intelligence Platforms: From Event Streams to Autonomous Insight"
  Patra & Vadgave, 2026

The removal effect of state s with respect to terminal outcome t is the
decrease in overall conversion rate when s is removed from the journey graph
(Eq. 8):

  removal_effect(s, t) = B(start, t) - B'(start, t)

where B is the absorption probability matrix of the original chain and B' is
the absorption probability matrix after removing state s.

Removal procedure (Section 5.4):
  1. Delete all edges into and out of s from the transition graph.
  2. Re-normalise transition probabilities from predecessor states of s.
  3. Recompute B' under the modified graph.

A high removal effect indicates that s lies on the dominant conversion path.

Note: removal effect is a structural property of the observed graph and is
not equivalent to causal effect.

Usage
-----
    python removal_effect.py
"""

import numpy as np


# ---------------------------------------------------------------------------
# Journey definition (same as markov_journey_model.py)
# ---------------------------------------------------------------------------

# States matching the paper's example funnel (Figure 2):
#   Transient: sign_up, feature_used, import_data, invite_teammate
#   Absorbing: converted (paid), dropped_off (churned)

TRANSIENT = ["sign_up", "feature_used", "import_data", "invite_teammate"]
ABSORBING = ["converted", "dropped_off"]

# Full transition matrix (rows = from transient states, cols = all states)
# Layout: [sign_up, feature_used, import_data, invite_teammate,
#          converted, dropped_off]
P_full = np.array([
    # from sign_up      -> feature_used(0.52), converted(0.02), dropped_off(0.46)
    [0.00, 0.52, 0.00, 0.00,  0.02, 0.46],
    # from feature_used -> sign_up(0.15), import_data(0.44), dropped_off(0.41)
    [0.15, 0.00, 0.44, 0.00,  0.00, 0.41],
    # from import_data  -> invite_teammate(0.70), converted(0.08), dropped_off(0.22)
    [0.00, 0.00, 0.00, 0.70,  0.08, 0.22],
    # from invite_teammate -> converted(0.71), dropped_off(0.29)
    [0.00, 0.00, 0.00, 0.00,  0.71, 0.29],
])

n_t = len(TRANSIENT)
n_a = len(ABSORBING)


# ---------------------------------------------------------------------------
# Helper: compute B from a given P_full
# ---------------------------------------------------------------------------

def compute_B(P: np.ndarray) -> np.ndarray:
    """Compute absorption probability matrix B = N * R from P (k x k+n_a)."""
    k = P.shape[0]  # number of transient states in this (possibly reduced) matrix
    Q_local = P[:, :k]
    R_local = P[:, k:]
    N_local = np.linalg.inv(np.eye(k) - Q_local)
    return N_local @ R_local


# ---------------------------------------------------------------------------
# Helper: remove state s_idx and return modified P
# ---------------------------------------------------------------------------

def remove_state(P: np.ndarray, s_idx: int) -> tuple[np.ndarray, list[str]]:
    """
    Remove transient state at s_idx.

    Steps:
      1. Zero out all edges into and out of s_idx.
      2. Re-normalise rows of predecessor states (those that had transitions
         into s_idx) so they remain row-stochastic.
      3. Return the modified matrix with the removed state's row deleted.

    Returns (P_modified, remaining_transient_states).
    """
    P_mod = P.copy()

    # Step 1 & 2: for every predecessor i of s_idx, redistribute
    # the probability mass that went to s_idx proportionally across
    # the remaining destinations.
    for i in range(n_t):
        mass_to_removed = P_mod[i, s_idx]
        if mass_to_removed > 0:
            # Zero out the edge to s_idx
            P_mod[i, s_idx] = 0.0
            # Total remaining outgoing mass from i
            remaining = P_mod[i, :].sum()
            if remaining > 0:
                # Re-normalise so row sums to 1
                P_mod[i, :] /= remaining
            else:
                # All transitions went to s_idx (degenerate): send directly to 'dropped_off'
                dropped_col = n_t + ABSORBING.index("dropped_off")
                P_mod[i, dropped_col] = 1.0

    # Step 3: delete row and column of s_idx from P
    # Remove column s_idx (from transient block)
    P_mod = np.delete(P_mod, s_idx, axis=0)   # delete row
    P_mod = np.delete(P_mod, s_idx, axis=1)   # delete column
    remaining_states = [s for i, s in enumerate(TRANSIENT) if i != s_idx]
    return P_mod, remaining_states


# ---------------------------------------------------------------------------
# Compute removal effects for all transient states
# ---------------------------------------------------------------------------

def main() -> None:
    # Baseline absorption probabilities from "sign_up" (start state = index 0)
    B_base = compute_B(P_full)
    start_idx = TRANSIENT.index("sign_up")
    baseline_conversion = B_base[start_idx, ABSORBING.index("converted")]

    print("=" * 60)
    print("Removal Effect Computation — BIP Journey Model Demo")
    print("=" * 60)
    print(f"\nBaseline conversion probability from 'sign_up': {baseline_conversion:.4f}")
    print("\nRemoving each transient state in turn:\n")

    print(f"  {'State':<22} {'B(start,conv) after removal':>28} {'Removal Effect':>16}")
    print("  " + "-" * 68)

    results = []
    for s_idx, state_name in enumerate(TRANSIENT):
        if state_name == "sign_up":
            # Removing the start state itself is degenerate; skip
            print(f"  {state_name:<22} {'(start state — skip)':>28} {'N/A':>16}")
            continue

        P_mod, _ = remove_state(P_full, s_idx)

        # After removal, start state is still sign_up, but now at a different index
        # (sign_up is always first and we only remove non-start states)
        new_start_idx = 0  # sign_up remains at index 0

        B_mod = compute_B(P_mod)
        new_conversion = B_mod[new_start_idx, ABSORBING.index("converted")]
        effect = baseline_conversion - new_conversion
        results.append((state_name, effect))
        print(f"  {state_name:<22} {new_conversion:>28.4f} {effect:>+16.4f}")

    # Rank by removal effect
    results_sorted = sorted(results, key=lambda x: x[1], reverse=True)
    print("\n--- States ranked by removal effect (highest = most critical) ---")
    for rank, (name, eff) in enumerate(results_sorted, 1):
        print(f"  {rank}. {name:<22}  removal_effect = {eff:+.4f}")

    print(
        "\n  NOTE: Removal effect is a structural property of the observed"
        "\n  graph. It is NOT equivalent to causal effect (Section 5.4)."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
