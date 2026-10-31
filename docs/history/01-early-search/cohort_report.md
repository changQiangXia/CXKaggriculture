# Current submission diagnosis (2026-09-16)

Read-only Kaggle snapshot; validation episodes are excluded from competitive rates.

## Submission 56260878
- episodes: 102 total; 101 public competitive; validation: 1
- outcomes: {'loss': 14, 'win': 85, 'tie': 2}; competitive win rate=0.851
- losses: 14
  - early 33: {'win': 31, 'loss': 2}
  - middle 34: {'win': 30, 'loss': 3, 'tie': 1}
  - late 34: {'loss': 9, 'win': 24, 'tie': 1}

## Submission 56257428
- episodes: 128 total; 127 public competitive; validation: 1
- outcomes: {'win': 74, 'loss': 46, 'tie': 7}; competitive win rate=0.610
- losses: 46
  - early 42: {'win': 37, 'loss': 5}
  - middle 42: {'loss': 20, 'win': 20, 'tie': 2}
  - late 43: {'win': 17, 'loss': 21, 'tie': 5}

## Loss callback diagnostics 56260878
- loss episodes=14, callback records=10066, max duration=0.527314, p99=0.011188, stderr records=0, calls/episode median=719.0

## Loss callback diagnostics 56257428
- loss episodes=46, callback records=5033, max duration=0.72414, p99=0.011254, stderr records=0, calls/episode median=0.0

## Largest competitive losses by absolute reward gap
56260878:
  - gap=7801 episode=109430701 rewards=[108430.0, 116231.0] time=2026-09-15T21:51:02.725000
  - gap=4466 episode=109438141 rewards=[80212.0, 84678.0] time=2026-09-15T22:18:59.210000
  - gap=2221 episode=109477519 rewards=[106389.0, 108610.0] time=2026-09-16T00:50:11.268000
  - gap=1962 episode=109399843 rewards=[114579.0, 112617.0] time=2026-09-15T19:50:12.073000
  - gap=1593 episode=109482442 rewards=[107256.0, 105663.0] time=2026-09-16T01:06:38.800000
  - gap=1349 episode=109519380 rewards=[76487.0, 75138.0] time=2026-09-16T03:14:39.429000
  - gap=1321 episode=109442363 rewards=[93912.0, 95233.0] time=2026-09-15T22:34:56.841000
  - gap=1128 episode=109416825 rewards=[83554.0, 84682.0] time=2026-09-15T20:58:56.110000
  - gap=1098 episode=109477570 rewards=[106231.0, 107329.0] time=2026-09-16T00:50:11.358000
  - gap=924 episode=109455722 rewards=[94280.0, 93356.0] time=2026-09-15T23:27:29.250000
56257428:
  - gap=6564 episode=109437616 rewards=[75953.0, 82517.0] time=2026-09-15T22:14:58.269000
  - gap=5600 episode=109392182 rewards=[89813.0, 95413.0] time=2026-09-15T19:17:49.372000
  - gap=3445 episode=109372791 rewards=[63940.0, 60495.0] time=2026-09-15T18:05:52.318000
  - gap=2971 episode=109518675 rewards=[74302.0, 77273.0] time=2026-09-16T03:14:38.414000
  - gap=2930 episode=109386768 rewards=[69725.0, 72655.0] time=2026-09-15T18:57:47.873000
  - gap=2665 episode=109502811 rewards=[107923.0, 105258.0] time=2026-09-16T02:14:36.764000
  - gap=2296 episode=109516516 rewards=[121732.0, 124028.0] time=2026-09-16T03:06:46.805000
  - gap=1857 episode=109396329 rewards=[145282.0, 147139.0] time=2026-09-15T19:34:11.477000
  - gap=1795 episode=109349480 rewards=[92060.0, 93855.0] time=2026-09-15T16:34:25.964000
  - gap=1720 episode=109491442 rewards=[148904.0, 150624.0] time=2026-09-16T01:34:39.331000
