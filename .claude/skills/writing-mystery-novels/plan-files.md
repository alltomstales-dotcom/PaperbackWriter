# The book plan (stages 2 and 3)

Eight files in `series/<slug>/bookN/plan/`. Write them in this order, one per turn, each under 2,000 words. `paperbackwriter check-plan bookN/plan` checks the caps and the digest.

## 01_solution_and_suspects.md

- **Decision:** the culprit, from the cast, on the page by one-fifth of the book, not the visible opposition, never the sleuth, companion or victim.
- **Method:** what was done, with what, how long it took.
- **Timeline** of the crime window, one clock, every time unique.
- **Suspect matrix,** six live suspects, one row each:

| | Motive and hard secret | Opportunity or gap | Lie the sleuth catches | Knowledge slip, with its innocent source | Strongest and weakest chapters |
|---|---|---|---|---|---|

Rules for the matrix:
- No suspect's row is thinner than the culprit's before the three-quarter mark.
- At least two innocent suspects have motive, method and access all documented on the page.
- The culprit's "lie the sleuth catches" cell is empty before the reveal, or the lie is covered at once by a smaller, comic confession.
- Every innocent suspect has a real lie that is caught, and a real reason for it.
- One **natural pair** of innocents share a secret, so a two-person theory can absorb the culprit's clues.
- **Hold-back:** the facts only the investigators know, and the public line.

## 02a_curve.md

A table, one row per chapter: the probability a sharp reader gives each suspect, the front-runner, and what moves the numbers.

Limits to design to:
- First third: culprit at or under .20 and never the front-runner. No suspect above .30.
- Middle third: culprit at or under .30. Two reversals of front-runner.
- At 70%: culprit at or under .35, with at least three suspects at .12 or more.
- Culprit not above .80 until the chapter before the reveal.

## 02b_clues.md

**Culprit clues,** each with:

| ID | Chapter | Clue as shown | Foreground (the louder event) | Innocent surface reading | Seems to point at | Reinterpreted in |
|---|---|---|---|---|---|---|

- State the spacing rule at the top: which chapters hold culprit clues, at most one per three chapters before two-thirds.
- **Mechanism and timing clues** point at nobody until reinterpreted. Give each a camouflage.
- **Herring clues,** one set per innocent suspect.
- At least five evidence clues in the first 60%. At most a quarter are documents. At most a third sit at the culprit's workplace or name the culprit's trade.
- One early clue shows the ground of the motive, shared among several people.

## 03_resolution_map.md

- **Mini-mysteries:** raised in, doubted in (new pressure, not recap), resolved in and how. None resolves in the chapter that raises it. Each gets two more chapters of doubt.
- **The false solution:** the sleuth's own deduction, argued aloud, acted on by the authorities, then cracked by a fact already on the page.
- **The proof chain** for the solution chapter: physical items only, each with the chapter that planted it.
- Every herring is resolved by the end. Arrest or consequence is stated.

## 04 and 05: chapter skeletons

The outline may be split over more files (04 to 07, six chapters each). Write each chapter as a `**Ch N. Title. When. Where.**` line followed by bullets, then run `paperbackwriter reader bookN/plan` (strips labels, clue IDs, `[D]` marks and cross-references into `plan/reader/`) and `paperbackwriter digest bookN/plan/reader`.

One paragraph per chapter: day, time and place, what happens, which clue IDs appear and behind what foreground, the new event, the ending. Vary the endings. Mark the sleuth's own decisions.

## canon.md

Setting, cast with ages and tics, access (doors, keys, routes), mechanism, tides or timetables, the crime-window timeline, every document's exact wording, motives, secrets and lies, the ending. For a series it adds to the bible and never contradicts it.

## audit.md (stage 3)

Two passes. Fixes written here override the earlier files.

1. **Your own pass.** At 30%, 50% and 70%, list only what the plan has put on the page so far. Rank the suspects the way the blind reader does: closed knowledge, who lied, who has a gap, whose alibi is too tidy, and genre priors (the helpful amateur, the witness who fixes the timeline, the comic character).
2. **A fresh reader's pass.** Build the reader outline and digest (`paperbackwriter reader`, then `paperbackwriter digest`): what a reader sees in each chapter, with clue IDs, "reinterpreted" notes and all planner comments removed. Give the batches to a fresh agent one at a time with the checkpoint prompt in `blind-read.md`, and score each checkpoint with `paperbackwriter gate`.

Pass when the culprit is outside the top two at 30% and 50%, at or under .35 at 70%, and the reader names real grounds for at least three suspects. Fail means redesign file 01, not rewording.
