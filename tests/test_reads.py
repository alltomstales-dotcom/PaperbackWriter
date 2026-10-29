import json
from pathlib import Path

import pytest

from paperbackwriter.reads import check_log, ranking, stage


def _folder(tmp_path: Path, upto: int) -> Path:
    for n in range(1, upto + 1):
        (tmp_path / f"ch{n:02d}.txt").write_text(f"Chapter {n}: T\n\nThe baker said the oven was cold in chapter {n}.\n")
    return tmp_path


def _log(folder: Path, after: int, suspects) -> Path:
    path = folder / f"log_ch{after:02d}.json"
    path.write_text(json.dumps({"after_chapter": after, "suspects": suspects}))
    return path


def test_a_log_with_exact_quotes_passes(tmp_path):
    folder = _folder(tmp_path, 3)
    log = _log(folder, 3, [
        {"name": "The baker", "p_culprit": 0.6, "evidence": [{"chapter": 2, "quote": "the oven was cold in chapter 2"}]},
        {"name": "The miller", "p_culprit": 0.4, "evidence": []},
    ])
    result = check_log(log)
    assert result["passed"], result["errors"]
    assert result["evidence_count"] == 1


def test_an_invented_quote_fails_the_log(tmp_path):
    folder = _folder(tmp_path, 3)
    log = _log(folder, 3, [{"name": "The baker", "p_culprit": 1.0,
                            "evidence": [{"chapter": 1, "quote": "the oven was hot"}]}])
    assert not check_log(log)["passed"]


def test_probabilities_must_sum_to_one(tmp_path):
    folder = _folder(tmp_path, 3)
    log = _log(folder, 3, [{"name": "A", "p_culprit": 0.5}, {"name": "B", "p_culprit": 0.4}])
    assert "Probabilities do not sum to one" in check_log(log)["errors"]


def test_a_chapter_past_the_checkpoint_on_disk_fails_the_log(tmp_path):
    folder = _folder(tmp_path, 4)
    log = _log(folder, 3, [{"name": "A", "p_culprit": 1.0}])
    assert not check_log(log)["passed"]


def test_a_finished_read_is_audited_on_quotes_only(tmp_path):
    folder = _folder(tmp_path, 5)
    log = _log(folder, 3, [{"name": "A", "p_culprit": 1.0,
                            "evidence": [{"chapter": 3, "quote": "oven was cold in chapter 3"}]}])
    assert check_log(log, finished=True)["passed"]
    bad = _log(folder, 3, [{"name": "A", "p_culprit": 1.0,
                            "evidence": [{"chapter": 5, "quote": "oven was cold in chapter 5"}]}])
    assert not check_log(bad, finished=True)["passed"]  # chapter 5 was not released at checkpoint 3


def test_ranking_finds_the_intended_answer(tmp_path):
    folder = _folder(tmp_path, 3)
    log = _log(folder, 3, [{"name": "Ana Rossi", "p_culprit": 0.5},
                           {"name": "Bo Penn", "p_culprit": 0.3},
                           {"name": "Cy Dunn", "p_culprit": 0.2}])
    assert ranking(log, "Bo Penn") == (2, 0.3)
    assert ranking(log, "Nobody Here") == (4, 0.0)


def test_stage_copies_only_up_to_the_checkpoint_and_never_backwards(tmp_path):
    chapters = tmp_path / "chapters"
    chapters.mkdir()
    for n in range(1, 25):
        (chapters / f"ch{n:02d}.txt").write_text(f"Chapter {n}: T\n\nx\n")
    read = tmp_path / "read"
    assert stage(chapters, read, 7) == 7
    assert sorted(p.name for p in read.glob("ch*.txt"))[-1] == "ch07.txt"
    assert stage(chapters, read, 12) == 5
    with pytest.raises(ValueError):
        stage(chapters, read, 7)


def _plan_read(tmp_path: Path):
    from paperbackwriter.reads import _sha
    plan = tmp_path / "plan"
    (plan / "digest").mkdir(parents=True)
    (plan / "01_solution_and_suspects.md").write_text("secret\n")
    for i, (lo, hi) in enumerate([(1, 7), (8, 12), (13, 17), (18, 21), (22, 24)], 1):
        (plan / "digest" / f"batch{i}.md").write_text(
            "\n\n".join(f"Chapter {n}: T\n\nAna Rossi bakes in chapter {n}." for n in range(lo, hi + 1)) + "\n")
    read = tmp_path / "read"
    read.mkdir()
    (read / "batch1.md").write_bytes((plan / "digest" / "batch1.md").read_bytes())
    ref = plan / "reference.json"
    ref.write_text(json.dumps({
        "candidate_directory": ".", "reader_folder": "../read", "intended_answer": "Bo Penn",
        "plan_sha256": {"01_solution_and_suspects.md": _sha(plan / "01_solution_and_suspects.md")},
        "digest_sha256": {p.name: _sha(p) for p in (plan / "digest").glob("batch*.md")}}))
    gate = plan / "gate.json"
    gate.write_text('{"checkpoints": []}')
    return plan, read, ref, gate


def test_plan_read_gate_releases_the_next_batch_when_the_answer_is_hidden(tmp_path):
    from paperbackwriter.reads import advance_plan_read
    plan, read, ref, gate = _plan_read(tmp_path)
    _log(read, 7, [{"name": "Ana Rossi", "p_culprit": 0.5,
                    "evidence": [{"chapter": 3, "quote": "Ana Rossi bakes in chapter 3"}]},
                   {"name": "Cy Dunn", "p_culprit": 0.3}, {"name": "Bo Penn", "p_culprit": 0.2}])
    record = advance_plan_read(ref, gate, 7)
    assert record["passed"] and record["rank"] == 3
    assert (read / "batch2.md").exists()


def test_plan_read_gate_fails_and_releases_nothing_when_the_answer_ranks_second(tmp_path):
    from paperbackwriter.reads import advance_plan_read
    plan, read, ref, gate = _plan_read(tmp_path)
    _log(read, 7, [{"name": "Ana Rossi", "p_culprit": 0.5}, {"name": "Bo Penn", "p_culprit": 0.3},
                   {"name": "Cy Dunn", "p_culprit": 0.2}])
    record = advance_plan_read(ref, gate, 7)
    assert not record["passed"]
    assert not (read / "batch2.md").exists()
    assert json.loads(gate.read_text())["stage"] == "FAILED_AT_7"


def test_plan_read_gate_refuses_a_changed_plan(tmp_path):
    from paperbackwriter.reads import advance_plan_read
    plan, read, ref, gate = _plan_read(tmp_path)
    (plan / "01_solution_and_suspects.md").write_text("changed\n")
    _log(read, 7, [{"name": "Ana Rossi", "p_culprit": 1.0}])
    with pytest.raises(ValueError):
        advance_plan_read(ref, gate, 7)
