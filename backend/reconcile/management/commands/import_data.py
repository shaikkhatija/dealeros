import csv
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand

from reconcile.cleaning import normalize_ref, parse_amount
from reconcile.models import Location, SystemARecord, SystemBEntry


class Command(BaseCommand):
    help = "Idempotently import locations and both system CSV files"

    def parse_date(self, raw):
        raw = (raw or "").strip()
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None

    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[3] / "data"
        location_count = 0
        with open(data_dir / "locations.csv", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                values = {key: (value or "").strip() for key, value in row.items()}
                Location.objects.update_or_create(
                    location_id=values["location_id"],
                    defaults={"org_id": values["org_id"], "name": values["location_name"]},
                )
                location_count += 1

        a_count = 0
        a_empty_values = 0
        with open(data_dir / "system_a.csv", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                values = {key: (value or "").strip() for key, value in row.items()}
                location = Location.objects.filter(location_id=values["location_id"]).first()
                amounts = {
                    "base": parse_amount(values["base_value"]),
                    "adjustment": parse_amount(values["adjustment"]),
                    "total": parse_amount(values["total_value"]),
                }
                a_empty_values += sum(value is None for value in amounts.values())
                SystemARecord.objects.update_or_create(
                    record_id=values["record_id"],
                    defaults={
                        "location": location,
                        "event_date": self.parse_date(values["event_date"]),
                        "event_date_raw": values["event_date"],
                        "category_code": values["category_code"],
                        "actor_id": values["actor_id"] or None,
                        "base_value": amounts["base"],
                        "base_value_raw": values["base_value"],
                        "adjustment": amounts["adjustment"],
                        "adjustment_raw": values["adjustment"],
                        "total_value": amounts["total"],
                        "total_value_raw": values["total_value"],
                        "state": values["state"],
                    },
                )
                a_count += 1

        b_count = 0
        b_empty_values = 0
        b_cleaned_refs = 0
        with open(data_dir / "system_b.csv", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                values = {key: (value or "").strip() for key, value in row.items()}
                location = Location.objects.filter(location_id=values["location_id"]).first()
                cleaned = normalize_ref(values["record_ref"])
                if cleaned != values["record_ref"]:
                    b_cleaned_refs += 1
                amount = parse_amount(values["value"])
                b_empty_values += amount is None
                SystemBEntry.objects.update_or_create(
                    entry_id=values["entry_id"],
                    defaults={
                        "record_ref_raw": values["record_ref"],
                        "record_ref": cleaned,
                        "location": location,
                        "recorded_on": self.parse_date(values["recorded_on"]),
                        "recorded_on_raw": values["recorded_on"],
                        "value": amount,
                        "value_raw": values["value"],
                        "label": values["label"],
                    },
                )
                b_count += 1

        self.stdout.write(
            f"Locations: {location_count} read, {Location.objects.count()} saved; "
            f"A: {a_count} read, {SystemARecord.objects.count()} saved; "
            f"B: {b_count} read, {SystemBEntry.objects.count()} saved; "
            f"values left empty: {a_empty_values + b_empty_values}; "
            f"refs cleaned: {b_cleaned_refs}"
        )
