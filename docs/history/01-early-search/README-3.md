# v37 premium-gated reservation candidate (EXP-175)

This candidate starts from frozen V37 and changes one policy condition: the
five-turn reservation horizon is enabled only at steps 288--695 when the public
farm similarity is at least 0.96 **and** at least one visible premium price is
elevated (`WOOL >= 80`, `STRAWBERRY >= 150`, or `MILK >= 100`). Otherwise it
keeps V37's four-turn horizon. No private opponent state or future observation
is read. It is an incubating local candidate; no Kaggle submission has been
made.
