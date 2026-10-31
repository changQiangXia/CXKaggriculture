# EXP-174 v37_hdss implementation report

The candidate is an executable copy of the frozen V37 parent plus a minimal H-DSS safety hook. `agent` delegates to the parent and then calls `apply_dss_profile`; no action can change unless an external state supplies a certificate with zero overflow, unchanged BUY/HIRE/PICKUP barriers, and at least a 50-coin conservative gain. Therefore the default and single-file fallback paths are exactly native V37 behavior.

`hdss.py` implements `DSSState`, `select_dss_profile`, `simulate_dss_block`, and `apply_dss_profile`. `simulate_dss_block` delegates to `engine_block_sim.py`, which invokes the installed Kaggriculture engine's unit, market, town, decay, and end-of-day primitives in production order. It clones public farms and shared state plus only the acting player's private view; an opponent private state is synthesized empty and omitted opponent actions default to PASS. This is a diagnostic replay, not a score oracle: shared opponent effects and unknown RNG are not inferred.

Validation performed:

- `python -m py_compile incubated_candidates/v37_hdss/main.py incubated_candidates/v37_hdss/hdss.py`
- Imported `main.py` directly by file path; parent and H-DSS symbols loaded and telemetry starts at `profile=native`.
- Synthetic ledger smoke test confirmed SELL quantities are capped by visible shed and `apply_dss_profile` returns an equal deep copy of the parent action.
- `python incubated_candidates/v37_hdss/test_engine_block_sim.py` passed four deterministic checks, including a one-step comparison against the production interpreter and a no-op opponent-private information-flow guard.
- Engine loading is lazy, so importing the candidate entry point does not emit environment warnings or incur engine setup unless a diagnostic replay is explicitly requested.
- Created `SHA256SUMS` and `v37_hdss.tar.gz` (archive SHA is regenerated after edits).

Additional replay parity check (2026-09-14): the candidate and frozen parent
were each fed all 719 decision observations from replay `108205627`. Their
actions were byte-for-byte identical at every state (`719/719`, zero
differences). This is a no-op safety result, not evidence of a score gain; the
candidate remains incubating until an engine-validated certificate can enable a
non-native profile.

The engine-backed block simulator and its four deterministic tests were added
after the initial report. Running `python test_engine_block_sim.py` produced
`engine_block_sim tests: PASS`; the refreshed archive includes `main.py`,
`hdss.py`, `engine_block_sim.py`, and the test file.

No Kaggle submission or upload was performed.
