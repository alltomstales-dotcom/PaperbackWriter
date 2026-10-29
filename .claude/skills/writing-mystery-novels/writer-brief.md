# Writer brief (stage 4) and fix pass (stage 6)

Save as `series/<slug>/bookN/WRITER_BRIEF.md`. Fill every `<...>`.

Draft in order, five chapters per drafting agent, one agent at a time. Each agent reads all earlier chapters.

## Template

```markdown
# Writer brief: <title>
B=<absolute path to series/<slug>/bookN>

You are drafting <genre and one-line description>. <Person and tense>, with <sleuth> as the detective. Tone: <tone from the bible>.

Read first, in full:
- <absolute path>/SERIES_BIBLE.md
- $B/plan/canon.md, 01, 02a, 02b, 03, 04, 05
- $B/plan/audit.md (its fixes override the earlier files)

Then read every chapter already in $B/chapters/ in full. Canon wins any conflict.

Your chapters: <N to M>. Output: $B/chapters/chNN.txt.
- First line "Chapter N: Title", a blank line, then plain prose. No markdown.
- "* * *" alone on a line for a real scene break only.
- Curly quotes.
- <1,900 to 2,200> words. One chapter per Write call. Keep your thinking short.

## Rules
- **Obey canon exactly:** names, clock times, objects, amounts, document wording. Invent nothing that touches the mystery. Log minor invented colour in $B/invented.md, one line each ("chN: detail").
- **Fair play.** Every clue listed for your chapter appears in scene, in the shape the clue map gives: an object seen, a document read, or a line spoken by someone present. It keeps its innocent reading and its camouflage. Never invisible, never spotlit.
- **New events.** Every chapter has a discovery, reversal, confrontation, danger or decision. No recap paragraphs. The past gets one line, with new spin.
- **Craft.** Specific sensory detail. Dialogue with subtext and distinct voices. Humour from character. Varied sentence and paragraph length. Varied chapter endings.
- **Budgets.** <motif> at most <n> times in the book. No signature phrase repeated across chapters. At most one simile in an emotional scene.
- **Avoid:** rule-of-three lists, "something shifted", "a beat", held breaths, everything "quiet".
- <Period books: nothing from the bible's banned list.>

## Hiding rules (read twice)
1. **<Culprit> is the killer. Until chapter <X> write them as the reader should see them: <their ordinary role>.** They appear in most chapters doing their job. They get exactly the clues the map assigns and nothing else. No lingering looks, no pauses before their answers, no one-line paragraphs about them, no glances from the sleuth.
2. **Every clue sits inside a louder scene.** In the middle of a paragraph. Never at the end of a paragraph or chapter, never the last line of dialogue in a scene.
3. **No narrator signposts.** Never "she would remember this later", "something nagged", "he filed it away". No chapter title names a clue. The sleuth either reads a clue the surface way, sincerely, or misses it because something else has their attention.
4. **Wrong theories, aloud and acted on.** The sleuth argues the cases the plan lists, for good reasons that are on the page. Never obtuse.
5. **Never stack.** Before chapter <Y>, no two <culprit>-pointing items within three chapters.
6. **Clear nobody in the chapter that raises them.** Follow the resolution map's raise, doubt and resolve chapters.
7. **The proof is physical.** No confession does evidentiary work.
8. **The culprit is never caught lying before the reveal.**
9. **Self-check before each save.** "If a very sharp reader stopped here, whom would they rank first, and is it who 02a_curve says?" If the culprit would be in the top two before chapter <X>, cut what put them there. Then list every line that touches the culprit and delete any the map does not require.

After your last chapter run wc -w on your files. Reply in under 100 words with any canon conflict or gap you worked around.
```

## Fix pass (stage 6, once)

- Build an **order list** from the blind read's verdict: one line per change, with chapter, the exact sentence, and the replacement or the instruction.
- Orders fix contradictions, plant motive ground, repair continuity. They never raise a clue's volume.
- Remove a known tell outright. Do not soften it and keep it.
- After any change to what a character says they do, search the whole book for lines that now contradict it.
- Reject any rewritten chapter that loses a named character or a clock time, or changes length by more than 80 words without an order saying so.

## Proofread (stage 7)

A fresh agent reads every line and reports **hard errors only**: contradictions of fact, time, place, name and order of events, each with the quote, the problem and an exact replacement. It builds its own working calendar first. It writes them to `bookN/proof_fixes.json` as `[{"file": "ch05.txt", "old": "...", "new": "..."}]`. Apply with `paperbackwriter proof bookN/proof_fixes.json` (try `--dry` first); a fix whose old text is not found exactly once is skipped and reported.
