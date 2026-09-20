import json

import pytest

from a3.store import Store


def test_roundtrip(tmp_path):
    path = tmp_path / "s.json"
    s = Store(path)
    s.put_card("exam", "001", {"id": "001", "due": "2026-09-21"})
    s.mark_seen("radar", "abc", "2026-09-20")
    s.log_run("exam", "2026-09-20T09:00:00", "3문제")
    s.save()

    again = Store(path)
    assert again.card("exam", "001")["due"] == "2026-09-21"
    assert again.is_seen("radar", "abc")
    assert again.recent_runs(1)[0]["task"] == "exam"


def test_missing_file_starts_empty(tmp_path):
    s = Store(tmp_path / "nope.json")
    assert s.deck("exam") == {}
    assert s.recent_runs() == []


def test_corrupt_file_raises_instead_of_silently_resetting(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        Store(path)


def test_run_log_is_bounded(tmp_path):
    s = Store(tmp_path / "s.json")
    for i in range(300):
        s.log_run("exam", f"t{i}", "x")
    assert len(s.data["runs"]) == 200
    assert s.data["runs"][-1]["at"] == "t299"


def test_seen_is_bounded(tmp_path):
    from a3 import store as store_mod

    s = Store(tmp_path / "s.json")
    limit = store_mod.MAX_SEEN_PER_NS
    for i in range(limit + 50):
        s.mark_seen("radar", f"k{i:05d}", f"2026-09-{(i % 28) + 1:02d}")
    assert len(s.data["seen"]["radar"]) <= limit


def test_save_is_atomic_and_readable(tmp_path):
    path = tmp_path / "nested" / "s.json"
    s = Store(path)
    s.put_card("exam", "001", {"id": "001"})
    s.save()
    assert json.loads(path.read_text(encoding="utf-8"))["cards"]["exam"]["001"]["id"] == "001"
    assert not list(path.parent.glob("*.tmp"))
