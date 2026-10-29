---
name: writing-mystery-novels
description: Use when planning, drafting, blind-reading, fixing, proofreading or releasing a fair-play mystery novel or series with PaperbackWriter — the staged route where the hiding is designed in the plan and measured by a reader who has never seen it.
---

# Writing Mystery Novels

## Overview

The route that took a book from blind-read scores of 2–3 (a local-model pipeline, nine runs) to 7–8 overall.

**Core principle:** hiding is designed in the plan and measured by a reader who has never seen the plan. Prose passes cannot add it.

Tools: the `paperbackwriter` command in this repository (`python -m paperbackwriter --help`).

## Where files go

```
series/<series-slug>/BUILD_BRIEF.md
series/<series-slug>/SERIES_BIBLE.md
series/<series-slug>/PROCESS.md, STATUS.md      from templates/
series/<series-slug>/bookN/plan/                plan files, reader/, reader/digest/
series/<series-slug>/bookN/WRITER_BRIEF.md
series/<series-slug>/bookN/chapters/chNN.txt
series/<series-slug>/bookN/blind_read/<date>/   logs and verdict, one folder per read
series/<series-slug>/bookN/release/
```

Every file an agent needs lives in the project, never in a scratch folder. Scratch folders get deleted.

## Stages

| # | Stage | Who | Output | Gate before moving on |
|---|---|---|---|---|
| 0 | Intake | You and the author | `BUILD_BRIEF.md` | Author confirms the brief. See `intake.md` |
| 1 | Series bible | You | `SERIES_BIBLE.md` | Author approves. No culprit in it |
| 2 | Book plan | You, one file at a time | `plan/` | Every file under 2,000 words: `paperbackwriter check-plan`. See `plan-files.md` |
| 3 | Plan read | A fresh agent | `blind_read/<date>-plan/` | `paperbackwriter gate` passes. See `blind-read.md` |
| 4 | Draft | Drafting agents, five chapters each, in order | `chapters/` | Each agent's self-check. See `writer-brief.md` |
| 5 | Blind read | A fresh agent, staged | `blind_read/<date>/` | Targets in `blind-read.md` |
| 6 | One fix pass | A drafting agent, from an order list | changed chapters | Read again. One pass only |
| 7 | Proofread | A fresh agent | `PROOF.md`, `proof_fixes.json` | Hard errors fixed by `paperbackwriter proof` |
| 8 | Final read and release | A fresh agent, then the build | `release/` | Read the final text, then `paperbackwriter export` |
| 9 | Record | You | `STATUS.md` | Scores, and what gave the culprit away |

Stages 3, 5, 7 and 8 need an agent that has seen nothing of the plan.

## Rules that outrank the stages

1. **Three suspects carry motive, method and access on the page.** A reader ranks the one suspect who has all three. Give the set to at least two others.
2. **The culprit's clues belong to someone else until three-quarters through.** Each has an innocent surface reading and sits inside a louder scene.
3. **The culprit is never caught lying before the reveal.** Red herrings are. A caught lie was the single strongest tell in every read.
4. **No stacking.** At most one culprit-pointing item in any three chapters before the two-thirds mark. No volunteered alibi, no tidy alibi.
5. **Nobody is cleared in the chapter that raises them.** Two decoys stay open to the reveal.
6. **The culprit is ordinary background.** On the page at least every third chapter, doing a job, never questioned, never lingered on.
7. **The solution uses only what was planted,** and the proof is physical. No confession does evidentiary work.
8. **Motive ground is planted early and shared.** Several people have the same grievance.
9. **One canon file.** Names, clock times, objects, amounts. Writers obey it and log anything they invent.
10. **The detective acts.** A consequential decision of their own by the quarter mark, and wrong theories argued aloud and acted on.
11. **Period books:** a banned list in the bible, and any real fact a clue leans on is checked against a source or replaced with an invented one.

## Stop rules

- **Plan read fails:** redesign the suspects. Do not draft.
- **Misdirection under 5 after the first blind read:** go back to stage 2. Do not edit sentences.
- **After one fix pass:** stop fixing. Repeated patch passes moved the culprit's probability .58, .62, .72 and misdirection 5, 5, 4.
- **Any edit after a blind read:** the score no longer describes the text. Read again before release.

## Who does what

| Job | Model | Why |
|---|---|---|
| Bible, plan, audit | The strongest reasoning model you have | Symmetric suspect design only came from here |
| Drafting, fix pass | A strong, cheaper drafting model | A first draft scored 6 where a small local model scored 2 |
| Blind read, proofread | A fresh agent on a strong model | Quotes verified 164 of 164. A proofread found 25 hard errors |
| Scoring or suspicion curves | Never a model grading its own book | Self-ratings said "hidden" when the blind reader said "obvious" |

Agents die at their output limit with nothing saved. One chapter per file write, one plan file per turn.

## Common mistakes

| Mistake | What happened last time |
|---|---|
| Fixing fair play by making clues louder | Culprit obvious from chapter 3 |
| Leaving a caught claim in "because the proof needs it" | The reader keyed on exactly that line |
| Editing a line to hide one tell | The edit created a new one two chapters earlier |
| Trusting an in-house score | 5.5 in house, 2 from the blind reader |
| Releasing after polish without a read | A book shipped two edits past its last read |
| Clue named in a chapter title | Reader flagged the title |
| A writer told the culprit with no rules for hiding | Narration winked: "She didn't see the lie" |

## Before release

- Categories chosen, narrowest true category first.
- In a series, keep it to three books or fewer.
- A fixed string from the last edit found in the exported EPUB.
- For a series opener: a free promotion sends readers to Book 2. Say so if Book 2 does not exist yet.
