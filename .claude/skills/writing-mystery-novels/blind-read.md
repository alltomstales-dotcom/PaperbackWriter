# Blind read (stages 3, 5 and 8)

The acceptance test. A reader who does not know the solution and cannot read ahead writes down whom they suspect at fixed points, with quotes.

## Set-up

- **A fresh agent on a strong model.** It has never seen the plan, the bible's book sections or an earlier draft. A reader who has seen any of them is void.
- **Staged release.** Copy chapters into `blind_read/<date>/` one batch at a time. Later chapters must not exist in that folder when a log is written.
- **Checkpoints:** about 30%, 50% and 70% of the book, the chapter before the reveal, and the end. For 24 chapters with the reveal at 22: chapters 7, 12, 17, 21, 24.
- **Verify every quote** by string search against the chapter files. An invented quote voids the log.

Release chapters with `paperbackwriter stage bookN/chapters bookN/blind_read/<date> <checkpoint>`; it refuses to go backwards. Verify each log with `paperbackwriter check-read <log> --answer "<culprit>"` (keep the answer out of the reader's sight). For the plan read, `paperbackwriter gate` does both and releases the next batch only on a pass.

## Reader prompt

```
You are a demanding mystery reader and editor. You are reading a novel you have
never seen, in batches. You do NOT know the solution, and the later chapters do
not exist yet on disk, so do not look for them.

Chapters are in <outdir> as chNN.txt. The first line is the chapter title, as a
reader sees it in the table of contents. Read every released chapter in full.

At each checkpoint write <outdir>/log_chNN.json (NN = last chapter read):
{
  "after_chapter": N,
  "suspects": [{"name": "...", "p_culprit": 0.0-1.0,
                "evidence": [{"chapter": n, "quote": "exact words from the text"}]}],
  "who_i_think_did_it": "...",
  "how_confident": "guess | lean | fairly sure | certain",
  "what_gave_it_away": "the specific moments, quoted, or 'nothing yet'",
  "craft_problems": [{"chapter": n, "quote": "...", "problem": "..."}]
}
p_culprit across suspects sums to 1. Every quote must be copied exactly from the
text. It will be verified by string search, and an invented quote voids the log.
Judge honestly: if the killer is obvious, say so and say when you knew.
Then STOP and reply with a two-line summary. The next batch will be released.

After the final chapter also write <outdir>/verdict.json:
{"fair_play": 1-10, "misdirection": 1-10, "prose": 1-10, "character": 1-10,
 "overall": 1-10, "when_culprit_became_obvious": chapter or null,
 "fair_play_notes": "...",
 "top_5_fixes": ["...concrete, with chapter numbers..."]}
```

For the plan read (stage 3), give the reader `plan/reader_digest.md` in three batches instead of chapters, ask for the same logs, and drop the prose and craft fields.

## Targets

| Measure | Target | First agent-built book | Christie, same reader |
|---|---|---|---|
| Culprit p at 30% | .30 or less, not first | .28 | .22 to .28 |
| Culprit p at 50% | .30 or less | .27 | about .45 at 60% (Styles) |
| Culprit p at 70% | .45 or less | .60 | under .80 until the reveal |
| Became obvious | No earlier than two chapters before the reveal | Chapter 14 of 20, reveal at 18 | At the reveal |
| Suspects at .15 or more at 70% | Three | Not recorded | Several, to the end |
| Fair play | 7 | 7 | 5 to 6 |
| Misdirection | 6 | 5 | 7 to 8 |
| Prose | 7 | 8 | 7 |
| Overall | 7 | 7 | 6 to 7 |

## Reading the result

- **"What gave it away" is the finding.** The scores only tell you which stage to return to.
- Culprit high at 30%: the plan stacks pointers early, or one suspect alone has motive, method and access. Back to plan file 01.
- A jump at one checkpoint: find the quoted lines. It is usually a claim that an earlier physical fact disproves, a volunteered alibi, or a verbal tic that echoes the method.
- Fair play low with hiding good: the culprit is over-hidden. Links between clues and culprit arrive late or off the page. Plant them earlier with innocent readings. Do not make them louder.
- Fair play and hiding trade against each other. Change one thing per pass and read again.

## Record every read

One line per read in `STATUS.md`: date, text read, overall, fair play, misdirection, prose, character, the chapter the culprit became obvious, and what gave it away.
