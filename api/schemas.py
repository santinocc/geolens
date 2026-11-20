"""The shapes of the data the API sends and receives (Pydantic models)."""
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Region(BaseModel):
    """A region as the API returns it."""
    id: UUID
    name: str
    geometry: dict  # GeoJSON, exactly as PostGIS produced it


class Scene(BaseModel):
    """A satellite scene found by a search. metres_away is set by the near-a-point search, covered_pct by the region search."""
    id: str
    acquired_at: datetime
    cloud_cover: float
    cog_url: str
    metres_away: float | None = None
    covered_pct: float | None = None


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"]
    # rings > points > exactly (lon, lat), each within the valid range
    coordinates: list[list[tuple[Annotated[float, Field(ge=-180, le=180)], Annotated[float, Field(ge=-90, le=90)]]]]


class RegionCreate(BaseModel):
    """What a client sends to create a region."""
    name: str = Field(min_length=1)
    geometry: PolygonGeometry
