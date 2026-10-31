# Working notes, in chronological order

These are the raw working notes kept while the competition ran.  They are
reproduced verbatim, in three phases, because the value of an archive like
this is being able to follow how the conclusions were reached — including the
dead ends.

```
01-early-search/       2026-09-12 .. 09-18    the initial candidate search
02-main-exploration/   2026-09-19 .. 09-29    the main exploration log
03-final-push/         2026-09-30 .. 10-02    endgame and post-mortem
```

**A note on dates.**  Files are grouped by the workspace modification time of
the note, which is normally the day it was written, but a handful were copied
or rewritten later and therefore sit in a later bucket than their content.
Where it matters the date is in the filename.  Many notes carry a
`_YYYYMMDD` suffix; trust that over the directory.

Also note that some files are not our words: several `*.md` files are
**transcripts of public Kaggle notebooks and discussions** saved for reading
offline.  Their provenance is in the file itself.

---

## The competition, briefly

**Kaggriculture** (Kaggle, Featured, $50,000): write an agent that farms a
10×10 board for 30 in-game days — crops, livestock, hired hands, and a shared
market with a second player.  Your score is your final bank.  Two agents play
each episode; episodes are matched continuously by skill rating, and the final
standing is a two-week Bradley-Terry rerun after submissions close.

Rules that shaped everything:

* **5 submissions per day, but only the latest 2 are tracked** — and those two
  are what the final rerun scores, so a new submission evicts an older one.
* Submissions closed **2026-09-30 23:59 UTC** (Beijing time 10-01 08:00).
* The leaderboard kept playing for two more weeks, to **2026-10-14 23:59 UTC**.

---

## How the work actually went

### Phase 1 — early search (09-12 .. 09-18)

Started from scratch with a hard constraint from the outset: five submissions
a day and only two live at a time, so every submission had to be earned.
The first working document (`KAGGRICULTURE_PROGRESS.md`, 09-12) set the
house rules — *no submission without explicit approval*, *record the
verified facts before proposing new candidates* — and those rules held for the
whole competition.

Work in this phase was dominated by **building a trustworthy local
evaluator**, because the ladder is slow and noisy: a fog-of-war replay
harness over the rust port of the official engine, panels of recorded
opponents, and eventually the realisation that *a recorded opponent cannot
react*, which makes naive win rates on a replay panel meaningless.  That
single insight — **the frozen-tape fidelity problem** — is the thread that
runs through the entire archive, all the way to the unresolved puzzle in the
retrospective.

Candidates chased here (V37/V43/V45/V48 lineages, premium gates, flood
variants, Q20/Q25 timing searches) mostly did not survive, but they produced
the evaluation protocol everything later relied on.

### Phase 2 — main exploration (09-19 .. 09-29)

The workspace consolidated into `farm2945_dev/`, and the notes become dense:
band-by-band win/loss tables, route searches, animal-service designs,
mechanism candidates, chimeric merges, public-notebook audits.

This is where the agent architecture stabilised: a **frozen action tape**
(720 recorded turns) with roughly sixty hand-written policy layers wrapped
around it to override market orders, routes, labour allocation and animal
choices.  Layer by layer the notes record which of those overrides paid for
themselves.

Two disciplines emerge repeatedly in these notes and both were vindicated
later:

* **fidelity filtering** — drop any episode where the frozen opponent did not
  get to play its game, or you are measuring starvation, not skill;
* **paired comparison** — evaluate two candidates on the same opponents, same
  worlds, same seeds.

### Phase 3 — endgame (09-30 .. 10-02)

See `../experiment-log.md` (the detailed log) and `../retrospective.md` (the
lessons).  Summary of the last 38 hours:

* 60 constants swept; all but one dead, inert or already correct;
* one genuine un-taken switch found, `V9_FERT_FIRST_DAY 14 → 12`, worth
  **+84 margin per game** (t = 5.10 across three independent opponent pools);
* it had been discarded earlier because the first sweep used **win/loss
  counts**, which threw away nearly all the signal;
* the three-constant variant `comb2b` was submitted and finished on **2098.7**
  (top 4.6% of 10,246 teams — silver-medal band);
* a direct self-play duel then produced the **opposite** ranking to the replay
  harness, and the ladder sided with the duel.  That contradiction is
  documented but unresolved.

---

## Where to look for what

| you want | read |
|---|---|
| the house rules, competition facts, submission log | `01-early-search/KAGGRICULTURE_PROGRESS.md` |
| how the evaluator was built and why fidelity matters | `01-early-search/` (eval protocol, local eval plan, monitor status) |
| band-by-band opponent tables, route and herd research | `02-main-exploration/` |
| the final 38 hours in detail | `../experiment-log.md` |
| what we got wrong and how we caught it | `../retrospective.md` |
| how to re-run the evaluation | `../reproducing.md` |
| exact engine constants | `../../reference/engine-rules.md` |

---

## 关于本目录里的失效链接

这些笔记是**原样保留**的工作记录，其中不少链接指向**当时工作机上的文件**
（`results.json`、`candidate_*.tar.gz`、`*.py` 等），这些文件没有随笔记一起归档，
所以链接会失效。统计：约 100 处，类型集中在 `.json`(29)、`.md`(28)、`.gz`(22)、`.py`(18)。

这是**有意的**：笔记的价值在于当时的推理过程，不在于链接可用。
阅读时把它们当作"当时我看了哪个文件"的注脚即可。

本仓库**新写的**导航文档（根目录 `README.md` 与 `docs/0*.md`）内部链接全部有效。

另外，部分笔记里含有当时的机器路径（`/root/autodl-tmp/...`）与容器配置，
那是历史事实记录，不代表当前或未来的运行环境。
