from datetime import date

from django.db import models
from django.db.models import Q

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators

from core.models import TimeStampedModel
from entities.models import LegalEntity


class Person(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    nationality = models.CharField(max_length=2, blank=True, help_text="Two-letter country code, e.g. LU")

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name_plural = "people"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MandateQuerySet(models.QuerySet):
    def active_on(self, day=None):
       return self.filter(period__contains=day or date.today())


class Mandate(TimeStampedModel):
    class Role(models.TextChoices):
        DIRECTOR = "DIRECTOR", "Director"
        MANAGER = "MANAGER", "Manager (gérant)"
        CHAIR = "CHAIR", "Chairperson"

    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="mandates")
    entity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name="mandates")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DIRECTOR)
    period = DateRangeField(
        help_text="Start is inclusive, end is exclusive. Leave the end empty for an ongoing mandate."
    )

    objects = MandateQuerySet.as_manager()

    class Meta:
        ordering = ["period"]
        constraints = [
            models.CheckConstraint(
                condition=Q(period__lower_inf=False),
                name="mandate_has_start_date",
            ),
            ExclusionConstraint(
                name="no_overlapping_same_mandate",
                expressions=[
                    ("person", RangeOperators.EQUAL),
                    ("entity", RangeOperators.EQUAL),
                    ("role", RangeOperators.EQUAL),
                    ("period", RangeOperators.OVERLAPS),
                ],
                violation_error_message="This person already holds this role at this entity during this period.",
            ),
            ExclusionConstraint(
                name="one_chair_at_a_time",
                expressions=[
                    ("entity", RangeOperators.EQUAL),
                    ("period", RangeOperators.OVERLAPS),
                ],
                condition=Q(role="CHAIR"),
                violation_error_message="This entity already has a chairperson during this period.",
            ),
        ]

    def __str__(self):
        return f"{self.person} – {self.get_role_display()} at {self.entity}"