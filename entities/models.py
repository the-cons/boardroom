from django.db import models
from django.db.models import F, Q

from core.models import TimeStampedModel


class LegalEntity(TimeStampedModel):
    class Kind(models.TextChoices):
        FUND = "FUND", "Fund"
        HOLDCO = "HOLDCO", "Holding company"
        SPV = "SPV", "Special purpose vehicle"
        MANAGER = "MANAGER", "Manager / GP"
        OTHER = "OTHER", "Other"

    class LegalForm(models.TextChoices):
        SA = "SA", "Société anonyme (S.A.)"
        SARL = "SARL", "Société à responsabilité limitée (S.à r.l.)"
        SCA = "SCA", "Société en commandite par actions (S.C.A.)"
        SCS = "SCS", "Société en commandite simple (SCS)"
        SCSP = "SCSP", "Société en commandite spéciale (SCSp)"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    legal_form = models.CharField(max_length=10, choices=LegalForm.choices)
    jurisdiction = models.CharField(max_length=2, default="LU", help_text="ISO 3166-1 alpha-2")
    rcs_number = models.CharField("RCS number", max_length=20, blank=True)
    incorporated_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "legal entities"
        constraints = [
            models.UniqueConstraint(
                fields=["jurisdiction", "rcs_number"],
                condition=~Q(rcs_number=""),
                name="uniq_rcs_number_per_jurisdiction",
            ),
        ]

    def __str__(self):
        return self.name


class Ownership(TimeStampedModel):
    parent = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name="holdings")
    child = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name="shareholders")
    percentage = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["parent", "child"], name="uniq_ownership_edge"),
            models.CheckConstraint(condition=~Q(parent=F("child")), name="ownership_not_self"),
            models.CheckConstraint(
                condition=Q(percentage__gt=0) & Q(percentage__lte=100),
                name="ownership_percentage_range",
            ),
        ]

    def __str__(self):
        return f"{self.parent} → {self.child} ({self.percentage}%)"