-- The newest scenes whose footprint touches a region.
-- Run:  psql -v region='Chiba city' -f db/queries/01-scenes-for-region.sql
SELECT s.id,
       s.acquired_at::date AS day,
       round(s.cloud_cover::numeric, 1) AS cloud
FROM scenes s
JOIN regions r ON ST_Intersects(s.footprint, r.geom)
WHERE r.name = :'region'
ORDER BY s.acquired_at DESC
LIMIT 5;