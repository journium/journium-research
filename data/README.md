# Data

Supporting datasets and simulation outputs for the paper.

## Directory Layout

```
data/
├── synthetic/
│   ├── sample_event_stream.jsonl   # 1 000 synthetic raw events (NSD input format)
│   └── derived_states.jsonl        # State-derived output from the NSD stage
└── simulation-outputs/             # CSV/JSON outputs produced by simulation scripts
```

## Synthetic Event Stream (`synthetic/sample_event_stream.jsonl`)

**Schema** (one JSON object per line):

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string (UUID) | Globally unique event identifier (used for idempotency) |
| `user_id` | string | Anonymous or authenticated user identifier |
| `session_id` | string | Browser/app session identifier |
| `event_name` | string | Raw event name (e.g. `sign_up`, `email_verified`) |
| `timestamp` | string (ISO 8601 UTC) | Event timestamp |
| `properties` | object | Arbitrary event properties |
| `platform` | string | `web` \| `ios` \| `android` |
| `tenant_id` | string | Tenant identifier (multi-tenancy, see ADR-007) |

**Generation:** Events are synthetically generated to represent a realistic signup-to-activation
funnel with the same transition probabilities used in the simulation scripts. User journeys
follow the absorbing Markov chain defined in `simulations/markov_journey_model.py`.

**Provenance:** Fully synthetic — no real user data. Safe for public distribution.

## Derived States (`synthetic/derived_states.jsonl`)

Output of the Normalization and State Derivation (NSD) stage (Section 4.1 of the paper).
Each line corresponds to one derived state event mapped from the raw event stream.

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Source raw event ID |
| `user_id` | string | User identifier |
| `raw_event` | string | Original event name |
| `semantic_state` | string | Derived semantic state |
| `lifecycle_state` | string | Derived lifecycle state |
| `timestamp` | string (ISO 8601 UTC) | Timestamp (carried from raw event) |

## Simulation Outputs (`simulation-outputs/`)

This directory is populated when you run the simulation scripts with output enabled.
It is intentionally left empty in the repository (tracked via `.gitkeep`).

To regenerate:
```bash
cd ../simulations
python markov_journey_model.py
```
