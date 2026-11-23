from decimal import Decimal

from django.http import JsonResponse

from .compare import compare
from .models import SystemARecord, SystemBEntry


def disagreements_api(request):
    org = (request.GET.get("org") or "").strip()
    if org not in ("ORG-A", "ORG-B"):
        return JsonResponse({"detail": "org must be ORG-A or ORG-B"}, status=400)

    a_rows = {}
    a_queryset = SystemARecord.objects.select_related("location").filter(location__org_id=org)
    for record in a_queryset:
        a_rows[record.record_id] = {
            "total": record.total_value,
            "location": record.location.location_id if record.location else None,
            "date": record.event_date.isoformat() if record.event_date else None,
        }

    b_rows = []
    b_queryset = SystemBEntry.objects.select_related("location")
    for entry in b_queryset:
        b_rows.append({
            "entry_id": entry.entry_id,
            "ref": entry.record_ref,
            "value": entry.value,
            "location": entry.location.location_id if entry.location else None,
            "date": entry.recorded_on.isoformat() if entry.recorded_on else None,
        })

    all_disagreements = compare(a_rows, b_rows)
    # A-side records and orphans are filtered by tenant ownership.
    # Matched rows use System A's location as the visible location.
    tenant_rows = []
    for row in all_disagreements:
        if row["reason"] == "ORPHAN_IN_B":
            orphan_location = row["b_location"]
            if orphan_location:
                from .models import Location
                if Location.objects.filter(location_id=orphan_location, org_id=org).exists():
                    tenant_rows.append(row)
        elif row["record_id"] in a_rows:
            tenant_rows.append(row)

    reason = (request.GET.get("reason") or "").strip()
    if reason:
        tenant_rows = [row for row in tenant_rows if row["reason"] == reason]

    def money_text(value):
        return str(value) if value is not None else None

    output = []
    for row in tenant_rows:
        a_value = money_text(row["a_value"])
        b_value = money_text(row["b_value"])
        difference = None
        if row["a_value"] is not None and row["b_value"] is not None:
            try:
                difference = str(row["b_value"] - row["a_value"])
            except (TypeError, ArithmeticError):
                difference = None
        output.append({
            "reason": row["reason"],
            "record_id": row["record_id"],
            "location": row["location"],
            "a_value": a_value,
            "b_value": b_value,
            "difference": difference,
        })

    sort = (request.GET.get("sort") or "").strip()
    if sort in ("value", "-value"):
        reverse = sort.startswith("-")
        output.sort(
            key=lambda row: (row["a_value"] is None, Decimal(row["a_value"]) if row["a_value"] is not None else Decimal("0")),
            reverse=reverse,
        )

    return JsonResponse(output, safe=False)

# Create your views here.
