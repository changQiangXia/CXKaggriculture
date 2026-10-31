# Kaggle API check (2026-09-12)

- Kaggle CLI 2.2.4 is installed in `/root/miniconda3/envs/kaggle-cli/bin/kaggle`; the default PATH instead resolves an older `/root/.local/bin/kaggle` (1.7.4.5).
- Credentials use the new token file `~/.kaggle/access_token` with mode `600`; no `kaggle.json` exists. The CLI 2.2.4 successfully reads this token.
- `kaggle competitions list -s Kaggriculture` succeeded; competition id 147734, entered=True, submissions today 0/5, submissions enabled, deadline 2026-09-30.
- `kaggle competitions submissions kaggriculture` reports no submissions yet.
- `kaggle competitions files kaggriculture` lists only `AGENTS.md` and `README.md` (downloaded into this folder).
- Top-200 leaderboard score observed: 2699.7 (200th of 200 rows returned by `--page-size 1000`).

Security: do not print or commit the token. A transient tool issue may have exposed credential-like strings in inter-agent traffic; rotate the token if account security requires it.

## Public baseline evidence

- `kaggle competitions team-submissions 16718819` shows the top team (Majkel1337) has public scores 3151.8 and 3122.1.
- Replay for submission 56148003 is downloadable (32 MB, 720 steps); its final rewards are 88723 and 99016. This can be used as a strong behavioral reference (12 farmhands, heavy WATER/HARVEST/CARE/FEED/COLLECT_FERTILIZER, dynamic BUY/SELL).
