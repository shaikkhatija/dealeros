import pytest
from django.test import Client

from reconcile.models import Location, SystemARecord


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
