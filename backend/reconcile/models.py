from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=32, unique=True)
    org_id = models.CharField(max_length=32)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.location_id} ({self.org_id})"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=32, unique=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.PROTECT)
    event_date = models.DateField(null=True, blank=True)
    event_date_raw = models.CharField(max_length=64, blank=True, default="")
    category_code = models.CharField(max_length=32, blank=True, default="")
    actor_id = models.CharField(max_length=32, null=True, blank=True)
    base_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    base_value_raw = models.CharField(max_length=64, blank=True, default="")
    adjustment = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    adjustment_raw = models.CharField(max_length=64, blank=True, default="")
    total_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_value_raw = models.CharField(max_length=64, blank=True, default="")
    state = models.CharField(max_length=32, blank=True, default="")


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=64, unique=True)
    record_ref_raw = models.CharField(max_length=64, blank=True, default="")
    record_ref = models.CharField(max_length=32, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.PROTECT)
    recorded_on = models.DateField(null=True, blank=True)
    recorded_on_raw = models.CharField(max_length=64, blank=True, default="")
    value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    value_raw = models.CharField(max_length=64, blank=True, default="")
    label = models.CharField(max_length=128, blank=True, default="")

# Create your models here.
