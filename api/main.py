"""The GeoLens API. Run from the project folder:

    .venv/bin/uvicorn api.main:app --port 8001 --reload

Interactive docs, generated from the code: http://localhost:8001/docs
"""
from contextlib import asynccontextmanager

from datetime import date
from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Query

from api import repository
from api.db import get_conn, open_pool
from api.schemas import Region, RegionCreate, Scene


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Code before the yield runs at startup, code after it at shutdown."""
    app.state.pool = open_pool()
    yield
    app.state.pool.close()


app = FastAPI(title="GeoLens API", lifespan=lifespan)


@app.get("/health")
def health(conn=Depends(get_conn)):
    """Checks that the API can reach the database."""
    conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/regions", response_model=list[Region])
def list_regions(conn=Depends(get_conn)):
    """All regions of interest, with their shapes as GeoJSON."""
    return repository.list_regions(conn)


@app.post("/regions", response_model=Region, status_code=201)
def create_region(region: RegionCreate, conn=Depends(get_conn)):
    """Create a region from a name and a GeoJSON polygon."""
    try:
        return repository.create_region(conn, region.name, region.geometry.model_dump())
    except psycopg.errors.CheckViolation as error:
        # Pydantic checked the shape of the JSON. The database checks the geometry itself.
        raise HTTPException(status_code=422, detail=f"The database rejected the region: {error.diag.constraint_name}")


@app.get("/scenes/near", response_model=list[Scene])
def scenes_near(
    lon: Annotated[float, Query(ge=-180, le=180)],
    lat: Annotated[float, Query(ge=-90, le=90)],
    meters: Annotated[float, Query(gt=0, le=500_000)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    conn=Depends(get_conn),
):
    """Scenes whose footprint comes within `meters` of a point, nearest first."""
    return repository.scenes_near(conn, lon, lat, meters, limit)


@app.get("/regions/{region_id}/scenes", response_model=list[Scene])
def scenes_for_region(
    region_id: UUID,
    date_from: Annotated[date | None, Query(alias="from")] = None,
    date_to: Annotated[date | None, Query(alias="to")] = None,
    max_cloud: Annotated[float | None, Query(ge=0, le=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    conn=Depends(get_conn),
):
    """Scenes that touch a region, newest first, with how much of the region each covers."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' must not be after 'to'")
    if not repository.region_exists(conn, region_id):
        raise HTTPException(status_code=404, detail="Region not found")
    return repository.scenes_for_region(conn, region_id, date_from, date_to, max_cloud, limit)
