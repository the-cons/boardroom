from django.contrib import admin

from .models import Mandate, Person


class MandateInline(admin.TabularInline):
    model = Mandate
    extra = 0
    autocomplete_fields = ["entity"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "email", "nationality"]
    search_fields = ["first_name", "last_name", "email"]
    inlines = [MandateInline]


@admin.register(Mandate)
class MandateAdmin(admin.ModelAdmin):
    list_display = ["person", "role", "entity", "start_date", "end_date"]
    list_filter = ["role", "entity"]
    autocomplete_fields = ["person", "entity"]
    list_select_related = ["person", "entity"]