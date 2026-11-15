from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.backends.postgresql.psycopg_any import DateRange

from entities.models import LegalEntity, Ownership
from people.models import Mandate, Person

K = LegalEntity.Kind
F = LegalEntity.LegalForm
R = Mandate.Role

ENTITIES = [
    # name,                          kind,      legal form, RCS number
    ("Alpha Fund SCSp",              K.FUND,    F.SCSP,     "B100001"),
    ("Alpha Holdco S.à r.l.",        K.HOLDCO,  F.SARL,     "B100002"),
    ("Alpha PropCo 1 S.à r.l.",      K.SPV,     F.SARL,     "B100003"),
    ("Alpha PropCo 2 S.à r.l.",      K.SPV,     F.SARL,     "B100004"),
    ("Beta Partners S.A.",           K.OTHER,   F.SA,       "B100005"),
    ("Gamma Capital SCA",            K.FUND,    F.SCA,      "B200001"),
    ("Gamma GP S.à r.l.",            K.MANAGER, F.SARL,     "B200002"),
    ("Gamma Lux Invest S.à r.l.",    K.SPV,     F.SARL,     "B200003"),
]

OWNERSHIPS = [
    # parent,                    child,                       %
    ("Alpha Fund SCSp",          "Alpha Holdco S.à r.l.",     100),
    ("Alpha Holdco S.à r.l.",    "Alpha PropCo 1 S.à r.l.",   100),
    ("Alpha Holdco S.à r.l.",    "Alpha PropCo 2 S.à r.l.",    60),
    ("Beta Partners S.A.",       "Alpha PropCo 2 S.à r.l.",    40),
    ("Gamma Capital SCA",        "Gamma Lux Invest S.à r.l.", 100),
]

PEOPLE = [
    # first, last, nationality
    ("Anna",   "Weber",  "LU"),
    ("Marc",   "Schmit", "LU"),
    ("Sophie", "Muller", "FR"),
    ("Luca",   "Rossi",  "IT"),
    ("Eva",    "Klein",  "DE"),
]

MANDATES = [
    # last name, entity,                     role,       start,             end (None = ongoing)
    ("Weber",  "Alpha Holdco S.à r.l.",      R.DIRECTOR, date(2024, 1, 1),  None),
    ("Schmit", "Alpha Holdco S.à r.l.",      R.DIRECTOR, date(2024, 1, 1),  None),
    ("Weber",  "Alpha Holdco S.à r.l.",      R.CHAIR,    date(2024, 1, 1),  date(2026, 1, 1)),
    ("Muller", "Alpha Holdco S.à r.l.",      R.CHAIR,    date(2026, 1, 1),  None),
    ("Schmit", "Alpha PropCo 1 S.à r.l.",    R.MANAGER,  date(2024, 3, 1),  None),
    ("Schmit", "Alpha PropCo 2 S.à r.l.",    R.MANAGER,  date(2024, 3, 1),  None),
    ("Rossi",  "Gamma GP S.à r.l.",          R.MANAGER,  date(2023, 6, 1),  None),
    ("Klein",  "Gamma Lux Invest S.à r.l.",  R.MANAGER,  date(2023, 6, 1),  date(2025, 7, 1)),
    ("Rossi",  "Gamma Lux Invest S.à r.l.",  R.MANAGER,  date(2025, 7, 1),  None),
]

class Command(BaseCommand):
    help = "Fill the database with a demo fund structure. Safe to run repeatedly."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all entities, people and mandates before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.reset()

        entities = self.seed_entities()
        self.seed_ownerships(entities)
        people = self.seed_people()
        self.seed_mandates(people, entities)
        self.seed_users()

        self.stdout.write(self.style.SUCCESS("Demo data ready."))

    # --- steps -------------------------------------------------------------

    def reset(self):
        Mandate.objects.all().delete()  # first: mandates PROTECT their persons
        Person.objects.all().delete()
        LegalEntity.objects.all().delete()  # ownerships go with them (CASCADE)
        self.stdout.write(self.style.WARNING("Deleted existing data."))

    def seed_entities(self):
        result = {}
        for name, kind, legal_form, rcs in ENTITIES:
            entity, created = LegalEntity.objects.update_or_create(
                jurisdiction="LU",
                rcs_number=rcs,
                defaults={"name": name, "kind": kind, "legal_form": legal_form},
            )
            result[name] = entity
            self.log(entity, created)
        return result

    def seed_ownerships(self, entities):
        for parent, child, percentage in OWNERSHIPS:
            ownership, created = Ownership.objects.update_or_create(
                parent=entities[parent],
                child=entities[child],
                defaults={"percentage": percentage},
            )
            self.log(ownership, created)

    def seed_people(self):
        result = {}
        for first, last, nationality in PEOPLE:
            person, created = Person.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={"nationality": nationality},
            )
            result[last] = person
            self.log(person, created)
        return result

    def seed_mandates(self, people, entities):
        for last, entity, role, start, end in MANDATES:
            mandate, created = Mandate.objects.get_or_create(
                person=people[last],
                entity=entities[entity],
                role=role,
                period=DateRange(start, end, bounds="[)"),
            )
            self.log(mandate, created)

    def seed_users(self):
        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING("DEBUG is off: not creating demo users."))
            return

        User = get_user_model()

        editors, _ = Group.objects.get_or_create(name="Editors")
        editors.permissions.set(
            Permission.objects.filter(content_type__app_label__in=["entities", "people"])
        )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(" created superuser admin / admin")

        for username, groups in [("editor", [editors]), ("viewer", [])]:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(username)
                user.save()
            user.groups.set(groups)
            self.log(user, created)

    def log(self, obj, created):
        label = self.style.SUCCESS("created") if created else "exists "
        self.stdout.write(f"  {label}  {obj}")