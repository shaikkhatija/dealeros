from decimal import Decimal


def compare(a_rows, b_rows):
    by_ref = {}
    for entry in b_rows:
        by_ref.setdefault(entry["ref"], []).append(entry)

    disagreements = []
    for ref, entries in by_ref.items():
        if ref not in a_rows:
            for entry in entries:
                disagreements.append({
                    "reason": "ORPHAN_IN_B",
                    "record_id": ref,
                    "entry_id": entry["entry_id"],
                    "a_value": None,
                    "b_value": entry["value"],
                    "location": entry["location"],
                    "a_location": None,
                    "b_location": entry["location"],
                    "a_date": None,
                    "b_date": entry["date"],
                })

    for record_id, a in a_rows.items():
        entries = by_ref.get(record_id, [])
        if not entries:
            disagreements.append({
                "reason": "MISSING_IN_B", "record_id": record_id,
                "entry_id": None, "a_value": a["total"], "b_value": None,
                "location": a["location"], "a_location": a["location"],
                "b_location": None, "a_date": a["date"], "b_date": None,
            })
            continue

        if any(entry["value"] is None for entry in entries):
            disagreements.append({
                "reason": "VALUE_MISMATCH", "record_id": record_id,
                "entry_id": entries[0]["entry_id"], "a_value": a["total"],
                "b_value": None, "location": a["location"],
                "a_location": a["location"], "b_location": entries[0]["location"],
                "a_date": a["date"], "b_date": entries[0]["date"],
            })
            continue

        if len(entries) > 1:
            total = sum((entry["value"] for entry in entries), Decimal("0"))
            if total != a["total"]:
                disagreements.append({
                    "reason": "DUPLICATE_IN_B", "record_id": record_id,
                    "entry_id": ",".join(entry["entry_id"] for entry in entries),
                    "a_value": a["total"], "b_value": total,
                    "location": a["location"], "a_location": a["location"],
                    "b_location": entries[0]["location"], "a_date": a["date"],
                    "b_date": entries[0]["date"],
                })
            continue

        entry = entries[0]
        if entry["value"] != a["total"]:
            disagreements.append({
                "reason": "VALUE_MISMATCH", "record_id": record_id,
                "entry_id": entry["entry_id"], "a_value": a["total"],
                "b_value": entry["value"], "location": a["location"],
                "a_location": a["location"], "b_location": entry["location"],
                "a_date": a["date"], "b_date": entry["date"],
            })
        if entry["location"] != a["location"]:
            disagreements.append({
                "reason": "LOCATION_MISMATCH", "record_id": record_id,
                "entry_id": entry["entry_id"], "a_value": a["total"],
                "b_value": entry["value"], "location": a["location"],
                "a_location": a["location"], "b_location": entry["location"],
                "a_date": a["date"], "b_date": entry["date"],
            })
        if entry["date"] != a["date"]:
            disagreements.append({
                "reason": "DATE_MISMATCH", "record_id": record_id,
                "entry_id": entry["entry_id"], "a_value": a["total"],
                "b_value": entry["value"], "location": a["location"],
                "a_location": a["location"], "b_location": entry["location"],
                "a_date": a["date"], "b_date": entry["date"],
            })

    return disagreements
