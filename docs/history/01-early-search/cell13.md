## 10. Reproduce, and attribution

Section 9 wrote `main.py` and rebuilt the submission archive **byte-for-byte**, asserting both sha256 values. That is the same archive that played the games in the table at the top — you can check the hash against the one printed there.

To point the acceptance suite at your own agent, the structure is small enough to re-implement: label seeds into worlds by truncating a V43 mirror game at step 145, keep one unseen seed per world, play both seats, bootstrap the paired margins at the world level.

### Attribution

- **[V43 "Recovering Lost Harvests"](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests)**, Ahmed Berat Özer, Apache-2.0 — embedded verbatim, all notices retained. It is the agent; this notebook is a shell around it.
- The step-0 round-trip **mechanism** is also Ahmed's, described in his public V45 notebook. The size sweep in section 5, and the finding that 70 sits on the far shoulder of the plateau, are mine.
- V43 itself carries attribution to thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Rayk Kretzschmar and Dmitrii Gluzdov; those notices are retained in the embedded source.
- Front-loading, the two-turn advance, the horizon sweep, the acceptance suite and the two traps are original work, 2026-09-15/16.
