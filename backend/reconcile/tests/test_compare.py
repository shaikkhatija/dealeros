from decimal import Decimal

from reconcile.cleaning import normalize_ref, parse_amount
from reconcile.compare import compare


def entry(entry_id="E1", ref="REC-1", value="100.00", location="L1", date="2026-01-01"):
    parsed = value if isinstance(value, Decimal) else (None if value is None else Decimal(value))
    return {"entry_id": entry_id, "ref": ref, "value": parsed, "location": location, "date": date}


def a(total="100.00", location="L1", date="2026-01-01"):
    return {"total": Decimal(total), "location": location, "date": date}


def test_missing_in_b():
    assert [r["reason"] for r in compare({"REC-1": a()}, [])] == ["MISSING_IN_B"]


def test_orphan_in_b():
    rows = compare({}, [entry(ref="REC-999")])
    assert [r["reason"] for r in rows] == ["ORPHAN_IN_B"]


def test_duplicate_in_b():
    rows = compare({"REC-1": a("100.00")}, [entry("E1", value="40"), entry("E2", value="50")])
    assert [r["reason"] for r in rows] == ["DUPLICATE_IN_B"]


def test_value_mismatch():
    rows = compare({"REC-1": a("100.00")}, [entry(value="90")])
    assert [r["reason"] for r in rows] == ["VALUE_MISMATCH"]


def test_blank_value_is_not_zero():
    rows = compare({"REC-1": a("100.00")}, [entry(value=None)])
    assert [r["reason"] for r in rows] == ["VALUE_MISMATCH"]
    assert rows[0]["b_value"] is None


def test_split_entries_summing_to_total_are_not_error():
    rows = compare({"REC-1": a("100.00")}, [entry("E1", value="40"), entry("E2", value="60")])
    assert rows == []


def test_messy_refs_normalize():
    assert normalize_ref("rec1034") == "REC-1034"
    assert normalize_ref("REC - 1070") == "REC-1070"
    assert normalize_ref("1112") == "REC-1112"


def test_indian_style_amount_and_blank():
    assert parse_amount("1,25,400.00") == Decimal("125400.00")
    assert parse_amount("") is None
    assert parse_amount("junk") is None


def test_clean_row_no_disagreement():
    assert compare({"REC-1": a()}, [entry()]) == []


def test_location_mismatch_is_caught():
    rows = compare({"REC-1": a(location="L1")}, [entry(location="L2")])
    assert [r["reason"] for r in rows] == ["LOCATION_MISMATCH"]


def test_date_mismatch_is_caught():
    rows = compare({"REC-1": a(date="2026-01-01")}, [entry(date="2026-01-02")])
    assert [r["reason"] for r in rows] == ["DATE_MISMATCH"]
