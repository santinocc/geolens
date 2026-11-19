-- How much of a region does each scene cover?
-- Run:  psql -v region='Tokyo Bay' -f db/queries/02-coverage-of-region.sql
-- Coverage % = area of the overlap / area of the whole region * 100, both measured in metres.
SELECT s.id,
       s.acquired_at::date AS day,
       round((100 * ST_Area(ST_Intersection(s.footprint, r.geom)::geography)
                  / ST_Area(r.geom::geography))::numeric, 1) AS covered_pct
FROM scenes s
JOIN regions r ON ST_Intersects(s.footprint, r.geom)
WHERE r.name = :'region'
ORDER BY covered_pct DESC, s.acquired_at DESC
LIMIT 6;
