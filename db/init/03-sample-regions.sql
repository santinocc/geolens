-- Three sample regions of interest, as simple rectangles (lon/lat, EPSG:4326).
-- ST_MakeEnvelope(xmin, ymin, xmax, ymax, srid): x is LONGITUDE, y is LATITUDE.
INSERT INTO regions (name, geom) VALUES
    ('Chiba city',   ST_MakeEnvelope(140.04, 35.55, 140.20, 35.68, 4326)),
    ('Tokyo Bay',    ST_MakeEnvelope(139.75, 35.30, 140.05, 35.65, 4326)),
    ('Narita area',  ST_MakeEnvelope(140.33, 35.72, 140.45, 35.82, 4326));
