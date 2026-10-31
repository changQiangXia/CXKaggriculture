# Engine block replay implementation

`engine_block_sim.py` provides `replay_block(obs, config, own_actions, opponent_actions=None, seed=0, detailed=True)` and `parity_compare(result, expected_obs)`. It loads Kaggriculture's installed engine source and invokes the production unit, market, town, decay, and end-of-day functions in their documented order. The input is bounded to one 72-step block.

The simulator clones all public farms and shared market/town state, then clones only `obs["private"]` for the acting seat. The counterpart receives a synthetic empty private state; omitted opponent actions are PASS. No nested opponent private data is traversed. An optional opponent action stream is explicitly offline public input and is marked in telemetry.

`hdss.simulate_dss_block` now delegates to this replay and remains diagnostic (`accepted=False` until a separate certificate). `test_engine_block_sim.py` runs three deterministic checks and currently passes.

Because Kaggriculture's market is shared, a public opponent action tape paired
with a synthetic empty opponent private state cannot reproduce that opponent's
SELL quantities or exact cash path. Such runs are intentionally limited to
own-state overflow and barrier diagnostics; they must not be presented as a
full replay parity result. Full parity requires the original replay's complete
private states and is therefore an offline audit artifact, never an input to
the deployed policy.
