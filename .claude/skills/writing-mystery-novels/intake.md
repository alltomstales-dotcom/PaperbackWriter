# Intake: "what are we building"

Stage 0. The output is `series/<slug>/BUILD_BRIEF.md`, confirmed by the user.

## How to run it

1. Fill in every row you can from what the user has already said, from memory, and from the last book's release folder.
2. Ask only for the rows marked **must ask** that are still empty. One round, four questions at most, each with a recommended answer first.
3. Give every other empty row a default and mark it "assumed".
4. Write the brief, show it, and correct it from the reply. Silence on an assumed row is not agreement: keep it marked "assumed" until the user says yes.

## The prompts

| # | Row | Ask it like this | Must ask? | Default if not asked |
|---|---|---|---|---|
| 1 | Format | "One book, or a series? How many?" | Yes | Three-book series |
| 2 | Pattern | "Which earlier book should this follow, and what should change?" | Yes | The last released mystery, unchanged |
| 3 | Place | "Where? I need a real, named, small place: a harbour, a square, a street." | Yes | None. Offer three |
| 4 | Time | "When? Today, or a year and a season?" | Yes | Contemporary |
| 5 | Sleuth | "Who investigates, what is their trade, and why do people tell them things?" | Yes | None. Offer three |
| 6 | Crime world | "Besides murder, what are people fighting over here?" | Yes | Land or inheritance |
| 7 | Companion | "Anyone you want beside the sleuth? Any animals?" | No | A foil who can go where the sleuth cannot, plus one animal |
| 8 | Tone and content | "How funny, how dark, how clean? Any faith or politics on the page?" | No | Wry, real menace, clean |
| 9 | Length | "How long?" | No | 24 chapters, about 50,000 words |
| 10 | Shelf | "Who is the reader and which three Amazon categories?" | No | Propose three, narrowest first, to be checked in the picker |
| 11 | Pen name and price | "Same pen name and opener price?" | No | As the last book |
| 12 | Series name and titles | "Any title in mind, or a pattern?" | No | Propose a series name on the place and three titles |
| 13 | Off-limits and must-haves | "Anything that must be in it, or must not?" | No | Real people never speak |
| 14 | Order of work | "Bible first, or straight to Book 1's plan?" | No | Bible first |
| 15 | Release plan | "When does Book 1 go out, and will Book 2 be ready before any free promotion?" | No | Open |
| 16 | Spoilers | "Do you want to know who did it, or read it cold?" | Yes, before stage 2 | Read it cold: plan summaries leave the culprit out |
| 17 | Done means | "What blind-read scores count as finished?" | No | Overall 7, fair play 7, prose 7, misdirection 6 |

## The brief

```markdown
# BUILD BRIEF: what we are building

Filled <date>. "User" marks what they said. "Assumed" marks a default not yet confirmed.

| # | Question | Answer | Source |
|---|---|---|---|
| 1 | Format | | |
...
| 17 | Done means | | |

## Approvals
- Series bible: user, before any plan is written.
- Book plan: user sees a spoiler-free summary unless row 16 says otherwise.
- Release: user, after the final blind read.
```

## The series bible (stage 1)

Sections, in this order. Template: `templates/SERIES_BIBLE.md`.

0. How to use it: canon, no culprit, real people never speak.
1. The promise: what every book delivers, and why an amateur investigates here.
2. Place and time: real fixed geography, invented places, the season of each book.
3. Period or local canon: law, money, travel, news, how a death is handled.
4. Banned list and language (period books), and how prejudice is handled.
5. Recurring cast: no shared first names, surnames or first initials. For the sleuth: why people talk to them, the wound, why the truth costs them, their rule, their limits, their voice.
6. Voice, tone, content, length.
7. Series signatures: three or four set pieces that recur, never the same way twice.
8. Series arc: threads across the books, in a table.
9. The books: premise, calendar and real anchors, the circle as public faces, the alibi engine.
10. Fact status: checked with a source, from general knowledge, check before a clue leans on it.
11. Decisions for the user.
