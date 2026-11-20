-- Areas the user cares about (drawn on the map).
CREATE TABLE regions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL CHECK (name <> ''),
    geom       geometry(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT regions_geom_valid CHECK (ST_IsValid(geom))
);
CREATE INDEX regions_geom_gist ON regions USING GIST (geom);

-- One satellite image from the catalog.
CREATE TABLE scenes (
    id           TEXT NOT NULL PRIMARY KEY,
    acquired_at  TIMESTAMPTZ NOT NULL,
    cloud_cover  REAL NOT NULL CHECK (cloud_cover >= 0 AND cloud_cover <= 100),
    footprint    geometry(Polygon, 4326) NOT NULL,
    cog_url      TEXT NOT NULL CHECK (cog_url LIKE 'https://%'),
    CONSTRAINT scenes_footprint_valid CHECK (ST_IsValid(footprint))
);
CREATE INDEX scenes_footprint_gist ON scenes USING GIST (footprint);
CREATE INDEX scenes_acquired_at ON scenes (acquired_at);

-- Distance queries measure in metres, so they cast the footprint to geography.
-- The cast hides the plain GiST index, so index the cast itself.
CREATE INDEX scenes_footprint_geog_gist ON scenes USING GIST ((footprint::geography));