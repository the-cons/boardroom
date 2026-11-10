from datetime import date

from django.db import models
from django.db.models import F, Q

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
        day = day or date.today()
        return self.filter(start_date__lte=day).filter(
            Q(end_date__isnull=True) | Q(end_date__gt=day)
        )


class Mandate(TimeStampedModel):
    class Role(models.TextChoices):
        DIRECTOR = "DIRECTOR", "Director"
        MANAGER = "MANAGER", "Manager (gérant)"
        CHAIR = "CHAIR", "Chairperson"

    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="mandates")
    entity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name="mandates")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DIRECTOR)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave empty if the mandate is ongoing.")

    objects = MandateQuerySet.as_manager()

    class Meta:
        ordering = ["start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gt=F("start_date")),
                name="mandate_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.person} – {self.get_role_display()} at {self.entity}"