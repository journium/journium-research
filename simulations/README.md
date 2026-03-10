# Simulations

Code that reproduces and demonstrates the formal results from the paper.

## Scripts

| Script | Paper Section / Equation | Description | Runtime |
|--------|--------------------------|-------------|---------|
| `markov_journey_model.py` | Section 5.1, Eq. 3–7 | Constructs the absorbing Markov chain journey model; computes fundamental matrix N, expected remaining steps, and absorption probability matrix B | < 1 s |
| `interestingness_scoring.py` | Section 5.5, Eq. 9 | Demonstrates the composite interestingness score on a synthetic set of detector findings; ranks findings into a prioritised insight feed | < 1 s |
| `removal_effect.py` | Section 5.4, Eq. 8 | Computes the removal effect for each transient state; identifies states on the dominant conversion path | < 1 s |

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
python interestingness_scoring.py
python removal_effect.py

# Interactive notebook:
jupyter notebook notebooks/journey_model_demo.ipynb
```

## Notes on the journey graph

All scripts use the same five-state signup-to-activation funnel:

```
sign_up → email_verified → profile_complete → feature_used → converted
                                                            ↘ dropped
```

Transition probabilities are synthetic but calibrated to be realistic for a
typical B2C SaaS onboarding funnel. They are defined inline in each script and
can be freely modified to explore different funnel shapes.
