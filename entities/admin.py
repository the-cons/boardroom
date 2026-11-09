from django.contrib import admin

from .models import LegalEntity, Ownership

class ShareholderInline(admin.TabularInline):
    model = Ownership
    fk_name = "child"
    extra = 0
    autocomplete_fields = ["parent"]
    verbose_name = "shareholder"
    verbose_name_plural = "shareholders (who owns this entity)"

class HoldingInline(admin.TabularInline):
    model = Ownership
    fk_name = "parent"
    extra = 0
    autocomplete_fields = ["child"]
    verbose_name = "holding"
    verbose_name_plural = "holdings (what this entity owns)"


@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    list_display = ["name", "kind", "legal_form", "jurisdiction", "rcs_number", "is_active"]
    list_filter = ["kind", "legal_form", "jurisdiction", "is_active"]
    search_fields = ["name", "rcs_number"]
    inlines = [ShareholderInline, HoldingInline]