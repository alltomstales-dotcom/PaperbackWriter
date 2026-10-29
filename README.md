# PaperbackWriter

A method and a small toolkit for writing **fair-play mystery novels with AI agents**, where the test of a book is a reader who has never seen the plan.

Most AI book pipelines fail the same way: the prose reads fine, and the killer is obvious by chapter three. Rewriting sentences does not fix that. PaperbackWriter treats hiding the culprit as a **design problem in the plan**, and measures it with **staged blind reads**. A fresh agent reads the book a few chapters at a time and writes down, with exact quotes, whom it suspects and how strongly.

> See **[howitworks.html](howitworks.html)** for an illustrated walk-through of the logic and the code.

## What's in the box

| Part | What it is |
|---|---|
| `.claude/skills/writing-mystery-novels/` | The method: stages, gates, stop rules, plan-file templates, the writer brief and the blind-reader prompt. Plain Markdown. Claude Code loads it as a skill when run in this repo, and any other agent can just read it. |
| `paperbackwriter/` | The Python tools that keep the method honest: outline stripping, staged release, quote verification, the plan-read gate, exact-string proofreading, EPUB/RTF/PDF export and optional audiobook narration. |
| `templates/` | `PROCESS.md`, `STATUS.md`, `AGENTS.md` and `SERIES_BIBLE.md` to drop into a new series folder. |
| `examples/` | A pronunciation file for the narrator. |

## The route

```
 0 Intake ─► 1 Series bible ─► 2 Book plan ─► 3 PLAN READ ─► 4 Draft ─► 5 BLIND READ ─► 6 One fix pass ─► 7 Proofread ─► 8 Final read + release
                                   ▲              │ fail                    │ misdirection < 5
                                   └──────────────┴─────────────────────────┘
                                        redesign the suspects; never polish sentences
```

- **Plan** (strongest reasoning model): solution and suspect matrix, a designed suspicion curve, a clue map where every culprit clue has an innocent reading and a louder scene to hide in, a resolution map, chapter skeletons and one canon file. Each file stays under 2,000 words.
- **Plan read:** a fresh agent reads only a stripped chapter outline, in five batches. At about 30% and 50% the true culprit must sit **outside the reader's top two**, and at 70% at or under **.35**. If it fails, redesign the plan. No prose has been written yet, so this costs little.
- **Draft** (a cheaper strong model): five chapters per agent, in order, obeying canon, with explicit hiding rules.
- **Blind read:** the same staged reader on the real chapters. Targets: overall 7, fair play 7, prose 7, misdirection 6.
- **One fix pass, then stop.** Repeated patch passes made the culprit *more* obvious every time (.58 → .62 → .72).
- **Proofread** by a fresh agent, hard errors only, applied as exact-string edits. Then a final read of the exact text being released.

## Results so far

These scores come from fresh AI blind readers, not sales:

| Approach | Blind-read overall | When the culprit became obvious |
|---|---|---|
| Earlier local-model pipeline, 9 runs | 2–3 / 10 | Usually by chapter 3 |
| This route, first book | 7 / 10 | Chapter 14 of 20 |
| This route, later books | 7–8 / 10 | The chapter before the reveal, or the reveal itself |
| Agatha Christie, same reader | 6–7 / 10 | At the reveal |

## Install

```bash
git clone https://github.com/alltomstales-dotcom/PaperbackWriter.git
cd PaperbackWriter
pip install -e ".[pdf]"          # add ,audio for narration; add ,dev for tests
paperbackwriter --help
```

The core tools use only the Python 3.10+ standard library. The PDF export needs `fpdf2` and a Unicode serif font (DejaVu Serif is found automatically on most Linux systems; otherwise pass `--font`). Narration needs `kokoro` (see the `audio` extra).

## Commands

| Command | Stage | What it does |
|---|---|---|
| `paperbackwriter reader bookN/plan` | 3 | Turns planner chapter files (`**Ch N. Title. When. Where.**` plus bullets) into reader outlines in `plan/reader/`. Strips labels, clue IDs, `[D]` decision marks and cross-references, and **refuses** if any planner mark is left. |
| `paperbackwriter digest bookN/plan/reader` | 3 | Splits the reader outline into five batches ending at the checkpoints (7, 12, 17, 21, 24 for 24 chapters). |
| `paperbackwriter check-plan bookN/plan` | 2–3 | Checks structure without printing spoilers: every file present and under 2,000 words, chapters covered exactly once, every digest batch identical to the stripped outline, writer brief present. |
| `paperbackwriter gate REF GATE CHECKPOINT` | 3 | Scores one plan-read checkpoint against an answer written down *before* the read, with plan and digest hashes, so the answer can't drift. Verifies every quote, then releases the next batch only on a pass. |
| `paperbackwriter stage CHAPTERS READ_DIR N` | 5, 8 | Copies chapters 1..N into a reader's folder. Later chapters never exist there early, and it refuses to go backwards. |
| `paperbackwriter check-read LOG [--answer NAME]` | 3, 5, 8 | Verifies a checkpoint log: probabilities sum to 1, only chapters through the checkpoint are on disk, and every quote is found by exact string search. `--finished` audits a completed read. |
| `paperbackwriter proof FIXES.json [--dry]` | 6, 7 | Applies `{"file", "old", "new"}` fixes. A fix whose old text isn't found exactly once is skipped and reported, never guessed. |
| `paperbackwriter export CHAPTERS --title T --author A` | 8 | Builds EPUB 3, RTF and a 6×9 PDF. `*italics*` are kept, and a `* * *` line is a scene break. |
| `paperbackwriter narrate CHAPTER OUT.wav` | after | Narrates a chapter with Kokoro TTS. `--pronunciations words.json` fixes names the phonemiser gets wrong. |

## A book's folder

```
series/<series-slug>/
  BUILD_BRIEF.md  SERIES_BIBLE.md  PROCESS.md  STATUS.md  AGENTS.md
  bookN/plan/                 01_solution_and_suspects.md  02a_curve.md  02b_clues.md
                              03_resolution_map.md  04..07_chapters_*.md  canon.md  audit.md
                              reader/  reader/digest/batch1..5.md
  bookN/WRITER_BRIEF.md
  bookN/chapters/ch01.txt …   first line "Chapter N: Title", then plain prose
  bookN/blind_read/<date>/    staged chapters, log_chNN.json, verdict.json
  bookN/release/
```

`series/` is in `.gitignore`, so your books stay private unless you choose otherwise.

## Using it with an agent

- **Claude Code:** open this repo, or copy `.claude/skills/writing-mystery-novels/` to `~/.claude/skills/`, and ask for a new series. The skill walks through intake, the bible and the plan, and tells you when to start fresh reader agents.
- **Codex or other agents:** point them at `templates/AGENTS.md` and the skill folder. Everything is plain Markdown.
- **People:** the same docs work as a checklist for a human writing room.

The **reader must be a fresh agent** every time. A reader that has seen any version of the plan, or an earlier read, is used up.

## Related work

- **[The Challenge and Reward of Fair Play in Narrative](https://arxiv.org/abs/2507.13841)** (Wagner, Keydar and Abend, 2025; first titled *Modeling Fair Play in Detective Stories with Language Models*) measures fair play in LLM-written detective stories. It finds they can be unpredictable but fail to balance surprise against fair play, which is the gap this project works on.
- **[WHODUNIT](https://arxiv.org/abs/2502.07747)** is a benchmark of mystery stories where models name the culprit. It tests the reverse problem, and could be used to check blind readers.
- **[ushironoko/novel-harness-skills](https://github.com/ushironoko/novel-harness-skills)** is a set of Claude Code skills for fair-play mysteries, in Japanese. After drafting, 12 parallel readers try to name the culprit before the reveal. PaperbackWriter differs in three ways: it reads in stages with quote verification, it reads the outline before any prose exists, and it allows one fix pass.
- **[NousResearch/autonovel](https://github.com/NousResearch/autonovel)** is an autonomous seed-to-audiobook novel pipeline driven by model-scored keep-or-retry loops. PaperbackWriter avoids self-scoring as a gate; in our measurements, models grading their own prose scored about three points high.
- **[Awesome-Story-Generation](https://github.com/yingpengma/Awesome-Story-Generation)** is a reading list of story-generation research.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Licence

MIT. See [LICENSE](LICENSE).
