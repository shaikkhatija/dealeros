import pytest
from django.test import Client

from reconcile.models import Location, SystemARecord, SystemBEntry


@pytest.mark.django_db
def test_org_a_api_does_not_return_org_b_locations():
    a_location = Location.objects.create(location_id="LOC-A", org_id="ORG-A", name="A")
    b_location = Location.objects.create(location_id="LOC-B", org_id="ORG-B", name="B")
    SystemARecord.objects.create(record_id="REC-A", location=a_location)
    SystemARecord.objects.create(record_id="REC-B", location=b_location)

    response = Client().get("/api/disagreements/", {"org": "ORG-A"})
    assert response.status_code == 200
    payload = response.json()
    assert all("LOC-B" not in str(row) for row in payload)
    assert all(row["record_id"] != "REC-B" for row in payload)


@pytest.mark.django_db
def test_org_b_api_does_not_return_org_a_locations():
    a_location = Location.objects.create(location_id="LOC-A", org_id="ORG-A", name="A")
    b_location = Location.objects.create(location_id="LOC-B", org_id="ORG-B", name="B")
    SystemARecord.objects.create(record_id="REC-A", location=a_location)
    SystemARecord.objects.create(record_id="REC-B", location=b_location)

    response = Client().get("/api/disagreements/", {"org": "ORG-B"})
    assert response.status_code == 200
    payload = response.json()
    assert all("LOC-A" not in str(row) for row in payload)
    assert all(row["record_id"] != "REC-A" for row in payload)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("org", "ascending", "descending"),
    [
        ("ORG-A", ["ORG-A-NEG-100", "ORG-A-NEG-2", "ORG-A-POS-3", "ORG-A-POS-20", "ORG-A-MISSING"],
         ["ORG-A-POS-20", "ORG-A-POS-3", "ORG-A-NEG-2", "ORG-A-NEG-100", "ORG-A-MISSING"]),
        ("ORG-B", ["ORG-B-NEG-100", "ORG-B-NEG-2", "ORG-B-POS-3", "ORG-B-POS-20", "ORG-B-MISSING"],
         ["ORG-B-POS-20", "ORG-B-POS-3", "ORG-B-NEG-2", "ORG-B-NEG-100", "ORG-B-MISSING"]),
    ],
)
def test_difference_sort_is_numeric_with_nulls_last_for_each_org(org, ascending, descending):
    location = Location.objects.create(
        location_id=f"LOC-{org}", org_id=org, name=org
    )
    cases = [
        ("NEG-100", "100.00", "0.00"),
        ("NEG-2", "20.00", "18.00"),
        ("POS-3", "10.00", "13.00"),
        ("POS-20", "10.00", "30.00"),
    ]
    for suffix, total, value in cases:
        record_id = f"{org}-{suffix}"
        SystemARecord.objects.create(
            record_id=record_id, location=location, total_value=total
        )
        SystemBEntry.objects.create(
            entry_id=f"ENTRY-{record_id}",
            record_ref=record_id,
            location=location,
            value=value,
        )

    missing_id = f"{org}-MISSING"
    SystemARecord.objects.create(
        record_id=missing_id, location=location, total_value="50.00"
    )

    client = Client()
    ascending_response = client.get(
        "/api/disagreements/", {"org": org, "sort": "value"}
    )
    descending_response = client.get(
        "/api/disagreements/", {"org": org, "sort": "-value"}
    )

    assert ascending_response.status_code == 200
    assert descending_response.status_code == 200
    assert [row["record_id"] for row in ascending_response.json()] == ascending
    assert [row["record_id"] for row in descending_response.json()] == descending
    assert ascending_response.json()[-1]["difference"] is None
    assert descending_response.json()[-1]["difference"] is None

    reason_response = client.get(
        "/api/disagreements/",
        {"org": org, "reason": "VALUE_MISMATCH", "sort": "value"},
    )
    assert [row["record_id"] for row in reason_response.json()] == ascending[:-1]
