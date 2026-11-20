-- Scenes whose footprint comes within some metres of a point, nearest first.
-- Run:  psql -v lon=141.6 -v lat=35.6 -v meters=50000 -f db/queries/03-scenes-near-point.sql
WITH p AS (SELECT ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography AS geog)
SELECT s.id,
       s.acquired_at::date AS day,
       round(ST_Distance(s.footprint::geography, p.geog)) AS metres_away
FROM scenes s, p
WHERE ST_DWithin(s.footprint::geography, p.geog, :meters)
ORDER BY metres_away, s.acquired_at DESC
LIMIT 5;