# list all recipes
default:
    @just --list

# start everything (foreground, with logs)
up:
    docker compose up --build

# start everything in the background
up-d:
    docker compose up --build -d

# stop everything (data is kept)
down:
    docker compose down

# follow the Django logs
logs:
    docker compose logs -f web

# run any manage.py command, e.g. `just manage showmigrations people`
manage *args:
    docker compose exec web python manage.py {{args}}

shell:
    just manage shell

migrate:
    just manage migrations

makemigrations *args:
    just manage makemigrations {{args}}

# open psql in the database container
psql:
    docker compose exec db psql -U boardroom

# DANGER: delete the database volume and start from scratch
reset-db:
    docker compose down -v

# seed demo data (add --reset to wipe first)
seed *args:
    just manage seed {{args}}
