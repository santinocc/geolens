"""The shapes of the data the API sends and receives (Pydantic models)."""
from uuid import UUID

from typing import Literal
from pydantic import BaseModel, Field


class Region(BaseModel):
    """A region as the API returns it."""
    id: UUID
    name: str
    geometry: dict  # GeoJSON, exactly as PostGIS produced it


class PolygonGeometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: list[list[tuple[float, float]]]  # rings > points > exactly (lon, lat)


class RegionCreate(BaseModel):
    """What a client sends to create a region."""
    name: str = Field(min_length=1)
    geometry: PolygonGeometry
