# How these books are written

A hand-off document for any agent (Claude, Codex or a person) picking up <Series Name>. It has no spoilers. Current progress is in `STATUS.md`, next to this file.

## The one rule about the author

If the author reads each book cold, **never put a culprit, a method or a twist in a message to them, in `STATUS.md`, in this file, in the bible or in the build brief.** Solutions live only in `bookN/plan/` and `bookN/blind_read/`. Report results as numbers and stages.

## What we are building

<Number> fair-play mysteries, about <24> chapters and <50,000> words each, set in <place, period>. The sleuth is <who>. Full answers are in `BUILD_BRIEF.md`. Series canon is in `SERIES_BIBLE.md`.

## Where things are

```
series/<slug>/
  PROCESS.md, STATUS.md, AGENTS.md   this hand-off
  BUILD_BRIEF.md                     what the author asked for, and what was assumed
  SERIES_BIBLE.md                    place, period, banned list, cast, voice. No spoilers
  bookN/plan/                        SPOILERS. Plan files, reader/ outlines, reader/digest/ batches
  bookN/WRITER_BRIEF.md              SPOILERS. Instructions for drafting agents
  bookN/chapters/chNN.txt            the book
  bookN/invented.md                  small details writers made up, one line each
  bookN/blind_read/<date>/           SPOILERS. Reader logs and verdicts
  bookN/release/                     final files
```

The method is in `.claude/skills/writing-mystery-novels/` of the PaperbackWriter repository (`SKILL.md`, `intake.md`, `plan-files.md`, `writer-brief.md`, `blind-read.md`). They are plain Markdown and any agent can read them.

## The route, one book at a time

| # | Stage | Who | Output | Gate |
|---|---|---|---|---|
| 1 | Plan | The strongest reasoning model available | plan files, `canon.md`, `audit.md` | Each file under 2,000 words (`paperbackwriter check-plan`) |
| 2 | Plan read | A fresh agent that has never seen the plan | logs in `blind_read/<date>-plan/` | Culprit outside the reader's top two at 30% and 50%, at or under .35 at 70% (`paperbackwriter gate`) |
| 3 | Draft | A drafting model, five chapters per agent, in order | `chapters/` | Each agent reads all earlier chapters and obeys canon |
| 4 | Blind read | A fresh agent, chapters released in stages | `blind_read/<date>/` | Overall 7, fair play 7, prose 7, misdirection 6 |
| 5 | One fix pass | A drafting agent, from a list of exact orders | changed chapters | One pass only, then read again |
| 6 | Proofread | A fresh agent, hard errors only | `PROOF.md`, `proof_fixes.json` | Fixes applied as exact-string edits (`paperbackwriter proof`) |
| 7 | Final read and release | A fresh agent, then the build | `release/` | The score must describe the final text (`paperbackwriter export`) |

## Stop rules

- Plan read fails: redesign the solution or the suspects. Do not draft.
- Misdirection under 5 on the first blind read: go back to the plan. Do not edit sentences.
- After one fix pass, stop fixing.
- Any edit after a blind read means the score no longer describes the text. Read again before release.

## Practical limits

- An agent that tries to write several chapters or plan files in one reply runs out of output and saves nothing. One chapter per file write.
- Keep every working file in the project. Scratch folders get deleted.

## Keeping the log

Add a dated line to `STATUS.md` at each stage change and each blind-read result. Scores and stages only.
