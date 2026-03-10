"""
markov_journey_model.py
=======================
Demonstrates the Absorbing Markov Chain journey model from Section 5.1 of:

  "Behavioral Intelligence Platforms: From Event Streams to Autonomous Insight"
  Patra & Vadgave, 2026

The script constructs a representative product-analytics journey graph,
estimates the fundamental matrix N = (I - Q)^{-1}, and computes:
  - Expected number of visits to each transient state (rows of N)
  - Expected remaining steps until absorption (row sums of N)
  - Absorption probability matrix B = N * R
    - B[i, 'converted'] = outcome conversion probability from state i
    - B[i, 'dropped']   = drop-off probability from state i

Usage
-----
    python markov_journey_model.py

No command-line arguments are required. The script prints matrices N and B
along with a plain-language interpretation of key values.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Journey definition
# ---------------------------------------------------------------------------
# States matching the paper's example funnel (Figure 2):
#   Transient: sign_up, feature_used, import_data, invite_teammate
#   Absorbing: converted (paid), dropped (churned)

TRANSIENT = ["sign_up", "feature_used", "import_data", "invite_teammate"]
ABSORBING = ["converted", "dropped"]

# ---------------------------------------------------------------------------
# Transition probability matrix P (rows = from, cols = to)
# Estimated from observed journey data (Section 4, Eq. 1)
# ---------------------------------------------------------------------------
#
# Layout: [sign_up, feature_used, import_data, invite_teammate,
#          converted, dropped]
#
# Row must sum to 1.0 (row-stochastic property, Eq. 2)

P_full = np.array([
    # from sign_up      -> feature_used(0.52), converted(0.02), dropped(0.46)
    [0.00, 0.52, 0.00, 0.00,  0.02, 0.46],
    # from feature_used -> sign_up(0.15), import_data(0.44), dropped(0.41)
    [0.15, 0.00, 0.44, 0.00,  0.00, 0.41],
    # from import_data  -> invite_teammate(0.70), converted(0.08), dropped(0.22)
    [0.00, 0.00, 0.00, 0.70,  0.08, 0.22],
    # from invite_teammate -> converted(0.71), dropped(0.29)
    [0.00, 0.00, 0.00, 0.00,  0.71, 0.29],
])

n_t = len(TRANSIENT)
n_a = len(ABSORBING)

# Sub-matrix Q: transient → transient (Eq. 3)
Q = P_full[:, :n_t]

# Sub-matrix R: transient → absorbing (Eq. 3)
R = P_full[:, n_t:]

# ---------------------------------------------------------------------------
# Validate row-stochastic property
# ---------------------------------------------------------------------------
row_sums = P_full.sum(axis=1)
assert np.allclose(row_sums, 1.0), f"Rows must sum to 1; got {row_sums}"

# ---------------------------------------------------------------------------
# Fundamental matrix  N = (I - Q)^{-1}   (Section 5.1, Eq. 5)
# ---------------------------------------------------------------------------
# N[i, j] = expected number of times the chain visits transient state j
#            when starting from transient state i, before absorption.
N = np.linalg.inv(np.eye(n_t) - Q)

# ---------------------------------------------------------------------------
# Expected remaining steps until absorption  t_i = sum_j N[i,j]  (Eq. 7)
# ---------------------------------------------------------------------------
t_vec = N.sum(axis=1)

# ---------------------------------------------------------------------------
# Absorption probability matrix  B = N * R   (Section 5.1, Eq. 6)
# ---------------------------------------------------------------------------
# B[i, k] = probability of being absorbed into absorbing state k
#            when starting from transient state i.
B = N @ R

# ---------------------------------------------------------------------------
# Display results
# ---------------------------------------------------------------------------
np.set_printoptions(precision=4, suppress=True, linewidth=100)

print("=" * 60)
print("Absorbing Markov Chain — BIP Journey Model Demo")
print("=" * 60)

print("\nTransient states:", TRANSIENT)
print("Absorbing states:", ABSORBING)

print("\n--- Sub-stochastic matrix Q (transient → transient) ---")
print(Q)

print("\n--- Absorption matrix R (transient → absorbing) ---")
print(R)

print("\n--- Fundamental matrix N = (I - Q)^{-1} ---")
print(N)
_header = "  " + "  ".join(f"{s:>18}" for s in TRANSIENT)
print(_header)
for i, row in enumerate(N):
    vals = "  ".join(f"{v:>18.4f}" for v in row)
    print(f"  {TRANSIENT[i]:<18}  {vals}")

print("\n--- Expected remaining steps until absorption (row sums of N) ---")
for i, ti in enumerate(t_vec):
    print(f"  From {TRANSIENT[i]:<20}: {ti:.4f} expected steps")

print("\n--- Absorption probability matrix B = N * R ---")
print(f"  {'State':<22} {'P(converted)':>14} {'P(dropped)':>12}")
print("  " + "-" * 50)
for i, row in enumerate(B):
    print(f"  {TRANSIENT[i]:<22} {row[0]:>14.4f} {row[1]:>12.4f}")

print("\n--- Key insight ---")
best_idx = int(np.argmax(B[:, 0]))
print(
    f"  Highest conversion probability from '{TRANSIENT[best_idx]}': "
    f"{B[best_idx, 0]:.1%}\n"
    f"  Lowest  conversion probability from '{TRANSIENT[np.argmin(B[:, 0])]}': "
    f"{B[np.argmin(B[:, 0]), 0]:.1%}"
)
print("=" * 60)
