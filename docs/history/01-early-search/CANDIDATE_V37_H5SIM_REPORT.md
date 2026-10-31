# V37 similarity gated horizon-5 candidate

## Variant

During steps 288–647, use a five-action sale reservation only while
`_r37_similarity(observation) >= 0.96`; otherwise use the frozen V37
four-action horizon. Steps 648–695 remain four-action. All existing route,
project, weed, capacity, purchase barrier, debt, quote and terminal layers are
unchanged.

## Results

- Against frozen V37, seeds 9001–9020 plus 1495252849, both seats: 22/22
  positive margins, mean +2218.95, minimum +740.
- Against Flex, seeds 9001–9010, both seats: 20/20 wins, mean +5048.8,
  minimum +2491.
- Against Thomas, seeds 9001–9010, both seats: 19/20 wins, mean +6272.6,
  minimum −556 (seed 9004, seat 1).
- Against Dmitrii, seeds 9001–9010, both seats: 20/20 wins, mean +6396.95,
  minimum +2739.
- All games completed 720 steps with no stderr.

The similarity gate reduces the Thomas counterexample from −942 in the
ungated horizon-5 variant to −556, but does not meet the zero-negative gate.
It remains local research only; no submission was made.

The live team rank is currently fluctuating around 170; the two active
submissions remain 56181773 and 56178383.

## Replay-seed regression check

Using the 15 seeds extracted from the latest real V37 loss set
(`1570771565`, `606276766`, `1170850889`, `1048630715`, `838513485`,
`594403442`, `1588330040`, `1946300122`, `679420063`, `1946686316`,
`1634969403`, `489957635`, `1670179817`, `1609194636`, `86191952`), the
similarity-gated candidate beat frozen V37 in all 30 seat/seed runs. The mean
margin was +2390.87 and the minimum was +443; all runs completed 720 steps.
This is useful evidence that the change addresses known loss seeds, but it
does not override the independent Thomas counterexample, so submission is
still withheld.
