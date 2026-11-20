"""The GeoLens API. Run from the project folder:

    .venv/bin/uvicorn api.main:app --port 8001 --reload

Interactive docs, generated from the code: http://localhost:8001/docs
"""
from contextlib import asynccontextmanager

from typing import Annotated

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
