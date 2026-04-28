# Simulations

Code that reproduces and demonstrates the formal results from the paper.

## Scripts

| Script | Paper Section / Equation | Description | Runtime |
|--------|--------------------------|-------------|---------|
| `markov_journey_model.py` | Section 5.1, Eq. 3–7 | Constructs the absorbing Markov chain journey model; computes fundamental matrix N, expected remaining steps, and absorption probability matrix B | < 1 s |
| `removal_effect.py` | Section 5.4, Eq. 8 | Computes the removal effect for each transient state; reproduces Figure 4 ranking | < 1 s |
| `simulate_trajectories.py` | Section 5.1.2, Figure 3 | Monte Carlo trajectory simulation (N=500K). Empirically verifies that under the strong Markov property `P(converted \| reached(s)) = B[s, converted]` and reproduces the Section 7.2 fact bundle values | ~3 s |
| `interestingness_scoring.py` | Section 5.5, Eq. 9 | Demonstrates the composite interestingness score on a synthetic set of detector findings; ranks findings into a prioritised insight feed; reproduces Table 1 | < 1 s |

## Notebooks

| Notebook | Description |
|----------|-------------|
| `notebooks/journey_model_demo.ipynb` | Interactive walkthrough of the absorbing Markov chain model with step-by-step visualisations |

## Requirements

```bash
pip install -r requirements.txt
```

Python >= 3.10 recommended. The scripts use only NumPy and SciPy (no
deep-learning frameworks or cloud SDKs required).

## Running

```bash
# From the simulations/ directory:

python markov_journey_model.py
python removal_effect.py
python simulate_trajectories.py
python interestingness_scoring.py

# Interactive notebook:
jupyter notebook notebooks/journey_model_demo.ipynb
```

## Notes on the journey graph

All scripts use the same four-state signup-to-activation funnel matching
Figure 2 of the paper:

```
sign_up → feature_used → import_data → invite_teammate ⇒ converted
   ↘           ↘             ↘             ↘          ⇒ dropped_off
```

Four transient states, two absorbing states (`converted`, `dropped_off`),
plus a back-edge `feature_used → sign_up` (re-visitation, dashed in Figure 2)
and a small direct conversion edge `sign_up → converted`. The transition
matrix is defined inline in `markov_journey_model.py` and can be freely
modified to explore different funnel shapes; `removal_effect.py` and
`simulate_trajectories.py` import from it.

Transition probabilities are synthetic but calibrated to be realistic for a
typical B2C SaaS onboarding funnel.

## Reproducibility cross-check

`simulate_trajectories.py` empirically verifies the closed-form computations
in `markov_journey_model.py`. With N=500,000 trajectories (seed=42), the
empirical conditional `P(converted | reached(s))` agrees with the formal
`B[s, converted]` to within ~0.001 absolute error for all four transient
states — the equality required by the strong Markov property when all
journeys share a common starting state.
