# PostgreSQL with the PostGIS extension, built from official sources only:
# the official postgres image plus the PostGIS package from PostgreSQL's own
# apt repository (already configured in this image). The popular postgis/postgis
# image is Intel-only, which would run emulated on Apple Silicon.
FROM postgres:17.12-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-17-postgis-3 \
 && rm -rf /var/lib/apt/lists/*
